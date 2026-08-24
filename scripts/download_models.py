import os
import sys
import urllib.request
from insightface.app import FaceAnalysis

def download_models():
    """
    Triggers InsightFace to download the buffalo_l model pack if it isn't already present.
    We point the root directory to our local 'models' folder.
    """
    model_root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    
    if not os.path.exists(model_root):
        os.makedirs(model_root)
        
    print(f"Downloading/verifying InsightFace models to: {model_root}")
    print("This may take a few minutes depending on your internet connection...")
    
    try:
        # By instantiating FaceAnalysis with our local root, InsightFace's internal
        # logic will download the zip and extract it to models/models/buffalo_l
        # Note: InsightFace creates a 'models' subfolder inside the root you give it.
        app = FaceAnalysis(name="buffalo_l", root=model_root)
        
        # Verify files exist
        expected_path = os.path.join(model_root, "models", "buffalo_l")
        if os.path.exists(expected_path) and len(os.listdir(expected_path)) > 0:
            print(f"[OK] InsightFace Models verified successfully at {expected_path}")
        else:
            print("\n[ERROR] Something went wrong. The InsightFace model directory is empty.")
            
        print("\nDownloading Anti-Spoofing Ensemble Models (PyTorch)...")
        anti_spoof_dir = os.path.join(model_root, "anti_spoofing", "pt_models")
        if not os.path.exists(anti_spoof_dir):
            os.makedirs(anti_spoof_dir)
            
        models_to_download = [
            ("2.7_80x80_MiniFASNetV2.pth", "https://github.com/minivision-ai/Silent-Face-Anti-Spoofing/raw/master/resources/anti_spoof_models/2.7_80x80_MiniFASNetV2.pth"),
            ("4_0_0_80x80_MiniFASNetV1SE.pth", "https://github.com/minivision-ai/Silent-Face-Anti-Spoofing/raw/master/resources/anti_spoof_models/4_0_0_80x80_MiniFASNetV1SE.pth")
        ]
        
        for model_name, url in models_to_download:
            path = os.path.join(anti_spoof_dir, model_name)
            if not os.path.exists(path):
                print(f"Downloading {model_name}...")
                urllib.request.urlretrieve(url, path)
                print(f"[OK] {model_name} downloaded.")
            else:
                print(f"[OK] {model_name} already exists.")
            
        print("\n[OK] All models are ready! You can now run the application completely offline.")

            
    except Exception as e:
        print(f"\n[ERROR] Error downloading models: {e}")
        sys.exit(1)

if __name__ == "__main__":
    download_models()
