import argparse
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForVision2Seq
from transformers.image_utils import load_image
from urllib.parse import urlparse
import os
import sys

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "HuggingFaceTB/SmolVLM-256M-Instruct"

# Charger modèle et processeur
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForVision2Seq.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16 if DEVICE == "cuda" else torch.float32,
).to(DEVICE)

#verifie si le chemin de l'imag eest une url
def is_url(path):
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False
#charge l'image pour le vlm
def load_input_image(image_path):
    try:
        if is_url(image_path):
            return load_image(image_path)
        else:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"File not found: {image_path}")
            return Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

#genere le prompt avec l'image à envoyer au vlm
def generate_prompt(image, instruction):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": instruction}
            ]
        },
    ]
    prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(text=prompt, images=[image], return_tensors="pt").to(DEVICE)
    generated_ids = model.generate(**inputs, max_new_tokens=500)
    generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
    return generated_texts[0]

def main():
    parser = argparse.ArgumentParser(description="SmolVLM CLI Tool: describe or OCR an image.")
    parser.add_argument("--image", type=str, required=True, help="Path or URL to the image")
    parser.add_argument("--action", choices=["describe", "ocr"], required=True, help="Action to perform")

    args = parser.parse_args()
    image_path = args.image
    action = args.action

    image = load_input_image(image_path)

    if action == "describe":
        instruction = "Can you describe this image?"
    elif action == "ocr":
        instruction = "What text do you see in this image?"
    else:
        print("Invalid action.")
        sys.exit(1)

    print("Processing...")
    output = generate_prompt(image, instruction)
    print("Result:\n")
    print(output)

if __name__ == "__main__":
    main()