# Deployment

Read this when the user is happy with the model and wants to *use* it — on a webcam, in a script, on a phone, or in a tiny web page.

## The trained weights

The file that matters is `runs/<name>/best.pt`. It's a self-contained PyTorch checkpoint — class names and architecture tag are baked in, so `predict.py` can load it anywhere torch is installed.

## Standalone predict script

`scripts/predict.py` is already the deployable artifact. Copy it next to `best.pt` and the user is done:
```bash
python predict.py best.pt new_photo.jpg
```

## Live webcam (classification or detection)

```python
import cv2, torch
from predict import load_checkpoint  # reuse the helper from predict.py

model, classes, task, imgsz = load_checkpoint("best.pt", torch.device("cpu"))
cap = cv2.VideoCapture(0)
while True:
    ok, frame = cap.read()
    if not ok:
        break
    # ... call model on frame as predict.py does, draw result, cv2.imshow ...
    if cv2.waitKey(1) == 27:  # Esc
        break
```
(Requires `pip install opencv-python`.)

## A 20-line web demo (Gradio)

```bash
pip install gradio
```
```python
import gradio as gr, torch
from PIL import Image
from predict import load_checkpoint
from torchvision.transforms import functional as TF

model, classes, task, imgsz = load_checkpoint("best.pt", torch.device("cpu"))

def infer(img: Image.Image):
    if task == "classify":
        # (mirror predict.py's classify path)
        ...
        return f"{classes[i]} ({prob[i]:.0%})"
    else:
        ...
        return drawn_image

gr.Interface(infer, gr.Image(type="pil"), "text" if task == "classify" else "image",
             title="My Vision Model").launch()
```

## Export to other runtimes

**TorchScript** (run without Python source):
```python
import torch
ckpt = torch.load("best.pt", map_location="cpu", weights_only=True)
# (rebuild the model exactly as predict.py does, load_state_dict, then:)
scripted = torch.jit.script(model)
scripted.save("model.torchscript")
```

**ONNX** (run in onnxruntime, mobile, browsers):
```python
dummy = torch.randn(1, 3, imgsz, imgsz)
torch.onnx.export(model, dummy, "model.onnx", opset_version=17,
                  input_names=["image"], output_names=["out"])
```
After ONNX export, inference needs only `pip install onnxruntime` — much lighter than full torch.

## Licensing

Everything in this skill's stack is permissively licensed: PyTorch and torchvision are BSD-3-Clause; open_clip_torch and its weights are Apache-2.0/MIT. Safe to embed in closed-source products.
