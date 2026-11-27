import base64
import json
import threading

import cv2
import numpy as np


_analyzer = None
_analyzer_lock = threading.Lock()


class FaceRecognitionError(Exception):
	pass


def _get_analyzer():
	global _analyzer

	if _analyzer is None:
		with _analyzer_lock:
			if _analyzer is None:
				try:
					from insightface.app import FaceAnalysis
				except ImportError as exc:
					raise FaceRecognitionError(
						"InsightFace is not installed on the server"
					) from exc

				analyzer = FaceAnalysis(
					name="buffalo_l",
					allowed_modules=["detection", "recognition"],
					providers=["CPUExecutionProvider"],
				)
				analyzer.prepare(ctx_id=-1, det_size=(640, 640))
				_analyzer = analyzer

	return _analyzer


def decode_image(image_base64):
	if not image_base64:
		raise FaceRecognitionError("No selfie image was provided")

	if "," in image_base64:
		image_base64 = image_base64.split(",", 1)[1]

	try:
		image_bytes = base64.b64decode(image_base64, validate=True)
	except (ValueError, base64.binascii.Error) as exc:
		raise FaceRecognitionError("The selfie image is not valid base64") from exc

	if not image_bytes:
		raise FaceRecognitionError("The selfie image is empty")

	image_array = np.frombuffer(image_bytes, dtype=np.uint8)
	image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
	if image is None:
		raise FaceRecognitionError("The selfie image could not be decoded")

	return image


def extract_embedding(image):
	faces = _get_analyzer().get(image)

	if not faces:
		raise FaceRecognitionError("No face was detected in the selfie")
	if len(faces) > 1:
		raise FaceRecognitionError("The selfie must contain exactly one face")

	embedding = np.asarray(faces[0].embedding, dtype=np.float32)
	if embedding.size == 0:
		raise FaceRecognitionError("A face embedding could not be generated")

	norm = np.linalg.norm(embedding)
	if not np.isfinite(norm) or norm == 0:
		raise FaceRecognitionError("A valid face embedding could not be generated")

	return (embedding / norm).tolist()


def cosine_similarity(left_embedding, right_embedding):
	left = np.asarray(left_embedding, dtype=np.float32)
	right = np.asarray(right_embedding, dtype=np.float32)

	if left.size != right.size or left.size == 0:
		raise FaceRecognitionError("Stored and captured embeddings are incompatible")

	left_norm = np.linalg.norm(left)
	right_norm = np.linalg.norm(right)
	if not np.isfinite(left_norm) or not np.isfinite(right_norm):
		raise FaceRecognitionError("Invalid face embedding")
	if left_norm == 0 or right_norm == 0:
		raise FaceRecognitionError("Invalid face embedding")

	similarity = float(np.dot(left, right) / (left_norm * right_norm))
	return max(-1.0, min(1.0, similarity))


def parse_embedding(embedding):
	if isinstance(embedding, list):
		return embedding

	try:
		return json.loads(embedding)
	except (TypeError, json.JSONDecodeError) as exc:
		raise FaceRecognitionError("The stored face embedding is invalid") from exc
