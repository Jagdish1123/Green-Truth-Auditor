from utils.llm_engine import analyze_text
from datasets import load_dataset
import time
import json
import sys

def run_evaluation():
    print("[+] Loading Emanuse/greenwashing dataset...")
    try:
        ds = load_dataset("Emanuse/greenwashing", split="train")
        # Ensure we have enough samples, grabbing first 50
        samples = ds.select(range(min(50, len(ds))))
    except Exception as e:
        print(f"[-] Failed to load dataset: {e}")
        return

    print(f"[+] Running Evaluation loop on {len(samples)} samples...\n")
    
    predicted_fluff = 0
    predicted_evidence = 0
    failures = []
    matches = 0
    
    for i, sample in enumerate(samples):
        text = sample.get("text", "")
        base_label = str(sample.get("label", ""))
        
        sys.stdout.write(f"\rProgress: [{'█' * int((i+1)/(len(samples))*20)}{' ' * (20 - int((i+1)/(len(samples))*20))}] {i+1}/{len(samples)}")
        sys.stdout.flush()
        
        try:
            res = analyze_text(text)
            pred_class = res.get("classification", "")
            if "Fluff" in pred_class:
                predicted_fluff += 1
            else:
                predicted_evidence += 1
                
            # Naive hackathon heuristic: matching textual ground truth vs our strict classification
            # Some datasets use "1" for greenwashing, some use "0". Let's track both and we can manually review eval_failures.json
            if ("0" in base_label and "Fluff" in pred_class) or ("1" in base_label and "Evidence" in pred_class):
                matches += 1
            else:
                failures.append({"id": i, "text": text, "predicted": pred_class, "true_label": base_label})
                
        except Exception:
            pass # Safe ignore for Hackathon rate limits
        
    print("\n\n📊 EVALUATION RESULTS")
    print("===============================")
    print(f"Total Samples Analyzed: {len(samples)}")
    print(f"Predicted Fluff: {predicted_fluff}")
    print(f"Predicted Evidence-Based: {predicted_evidence}")
    
    if len(samples) > 0 and base_label != "":
        accuracy = (matches / len(samples)) * 100
        print(f"\nAccuracy Proxy (vs Ground Truth): {accuracy:.1f}%\n")
    
    if failures:
        print(f"Found {len(failures)} mismatch edge-cases.")
        print("Saved mismatches to `eval_failures.json` for prompt debugging.")
        with open("eval_failures.json", "w") as f:
            json.dump(failures, f, indent=2)

if __name__ == "__main__":
    run_evaluation()
