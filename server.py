"""
S.C.C Web Server - Subway Crowd Control
Flask 백엔드: YOLOv11 감지 + REST API + MJPEG 스트림

엔드포인트:
  GET  /api/status       → 혼잡도 상태
  POST /api/config       → 최대 인원 설정
  POST /api/start        → 감지 시작
  POST /api/stop         → 감지 중지
  POST /api/demo/start   → 데모 모드 시작
  GET  /video_feed       → MJPEG 카메라 스트림 (관리자용)
"""

from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
import threading
import time
import os

app = Flask(__name__)
CORS(app)

# ─── 공유 상태 ───────────────────────────────────────────────
state = {
    "running": False,
    "head_count": 0,
    "max_people": 50,
    "last_updated": None,
    "camera_error": False,
}
state_lock = threading.Lock()

# 최신 프레임 버퍼 (MJPEG 스트림용)
frame_lock = threading.Lock()
latest_frame = None   # JPEG bytes


# ─── YOLOv11 감지 루프 ───────────────────────────────────────
def detection_loop():
    global latest_frame
    try:
        import cv2
        import pygame
        from ultralytics import YOLO

        pt_path = os.path.join(os.path.dirname(__file__), "e150b16p30.pt")
        model = YOLO(pt_path)

        pygame.mixer.init()
        is_audio_playing = False

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            with state_lock:
                state["camera_error"] = True
                state["running"] = False
            return

        print("[S.C.C] 감지 시작 (YOLOv11)")

        while True:
            with state_lock:
                if not state["running"]:
                    break
                max_ppl = state["max_people"]

            ret, frame = cap.read()
            if not ret:
                with state_lock:
                    state["camera_error"] = True
                break

            # YOLOv11 추론
            results = model(frame, verbose=False)[0]
            head_count = len(results.boxes)

            # ── 바운딩박스 + 인원 수 오버레이 ──────────────
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                label = model.names[cls]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            status_color = (0, 0, 255) if head_count > max_ppl else (0, 255, 0)
            cv2.putText(frame, f"Count: {head_count} / {max_ppl}",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 2)

            # ── 프레임을 JPEG로 인코딩해 버퍼에 저장 ───────
            _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            with frame_lock:
                latest_frame = jpeg.tobytes()

            # ── 상태 업데이트 ────────────────────────────────
            with state_lock:
                state["head_count"] = head_count
                state["last_updated"] = time.time()
                state["camera_error"] = False

            # ── 안내방송 ─────────────────────────────────────
            if not is_audio_playing and head_count > max_ppl:
                def play_audio():
                    nonlocal is_audio_playing
                    pygame.mixer.music.load("./announcements/ttswomanEng.mp3")
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        continue
                    is_audio_playing = False
                is_audio_playing = True
                threading.Thread(target=play_audio, daemon=True).start()

        cap.release()
        pygame.mixer.quit()
        with frame_lock:
            latest_frame = None
        print("[S.C.C] 감지 중지")

    except Exception as e:
        print(f"[S.C.C] 감지 오류: {e}")
        with state_lock:
            state["running"] = False
            state["camera_error"] = True
        with frame_lock:
            latest_frame = None


# ─── MJPEG 스트림 제너레이터 ────────────────────────────────
def generate_frames():
    """최신 프레임을 multipart/x-mixed-replace 형식으로 스트리밍"""
    while True:
        with frame_lock:
            frame = latest_frame

        if frame is None:
            # 감지 중이 아니면 빈 응답 대신 잠깐 대기
            time.sleep(0.1)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame +
            b"\r\n"
        )
        time.sleep(0.033)  # ~30fps 캡


# ─── API 엔드포인트 ──────────────────────────────────────────

@app.route("/video_feed")
def video_feed():
    """MJPEG 스트림 — <img src="http://localhost:5000/video_feed"> 로 사용"""
    return Response(
        stream_with_context(generate_frames()),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/api/status", methods=["GET"])
def get_status():
    with state_lock:
        s = dict(state)

    max_ppl = s["max_people"]
    count = s["head_count"]
    ratio = count / max_ppl if max_ppl > 0 else 0

    if ratio >= 1.0:
        level, level_en = "매우 혼잡", "very_crowded"
    elif ratio >= 0.7:
        level, level_en = "혼잡", "crowded"
    elif ratio >= 0.4:
        level, level_en = "보통", "moderate"
    else:
        level, level_en = "여유", "comfortable"

    return jsonify({
        "running": s["running"],
        "head_count": count,
        "max_people": max_ppl,
        "ratio": round(ratio, 3),
        "level": level,
        "level_en": level_en,
        "camera_error": s["camera_error"],
        "last_updated": s["last_updated"],
        "timestamp": time.time(),
        "has_feed": latest_frame is not None,
    })


@app.route("/api/config", methods=["POST"])
def set_config():
    data = request.get_json()
    max_ppl = data.get("max_people")
    if not isinstance(max_ppl, int) or max_ppl <= 0:
        return jsonify({"error": "유효한 최대 인원을 입력하세요 (양의 정수)"}), 400
    with state_lock:
        state["max_people"] = max_ppl
    return jsonify({"success": True, "max_people": max_ppl})


@app.route("/api/start", methods=["POST"])
def start_detection():
    with state_lock:
        if state["running"]:
            return jsonify({"error": "이미 실행 중입니다"}), 400
        state["running"] = True
        state["camera_error"] = False
    threading.Thread(target=detection_loop, daemon=True).start()
    return jsonify({"success": True, "message": "감지를 시작했습니다"})


@app.route("/api/stop", methods=["POST"])
def stop_detection():
    with state_lock:
        state["running"] = False
    return jsonify({"success": True, "message": "감지를 중지했습니다"})


# ─── 데모 모드 ───────────────────────────────────────────────
def demo_loop():
    import random
    count = 10
    print("[S.C.C] 데모 모드 실행 중...")
    while True:
        with state_lock:
            if not state["running"]:
                break
            count = max(0, min(state["max_people"] + 10,
                               count + random.randint(-3, 4)))
            state["head_count"] = count
            state["last_updated"] = time.time()
        time.sleep(1.5)


@app.route("/api/demo/start", methods=["POST"])
def start_demo():
    with state_lock:
        if state["running"]:
            return jsonify({"error": "이미 실행 중입니다"}), 400
        state["running"] = True
        state["camera_error"] = False
    threading.Thread(target=demo_loop, daemon=True).start()
    return jsonify({"success": True, "message": "데모 모드 시작"})


# ─── 실행 ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 45)
    print("  S.C.C Web Server")
    print("  관리자: admin.html")
    print("  승객:   passenger.html")
    print("  스트림: http://localhost:5000/video_feed")
    print("=" * 45)
    # threaded=True 필수 — MJPEG 스트림과 API 동시 처리
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)