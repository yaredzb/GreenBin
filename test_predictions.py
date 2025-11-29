import sys
import os
sys.path.append(os.getcwd())

from services.predictor import OverflowPredictor
import storage

bins = storage.load_bins()
history = storage.load_history()

predictor = OverflowPredictor()
predictions = predictor.predict(bins, history)

print(f"Total bins: {len(bins)}")
print(f"Total predictions: {len(predictions)}")
print("\nFirst 10 predictions:")
for i, (hours, b) in enumerate(predictions[:10]):
    print(f"{i+1}. Bin {b.id}: fill={b.fill_level}%, type={b.waste_type}, hours_remaining={hours:.2f}")
