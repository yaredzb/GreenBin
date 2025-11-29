# services/predictor.py
from structures.min_heap import MinHeap
import datetime

class OverflowPredictor:
    def __init__(self):
        pass

    def predict(self, bins, history):
        """
        Predicts when bins will overflow based on historical fill rates.
        Uses actual historical data to calculate fill rates per bin.
        Returns a list of (hours_remaining, bin) tuples, sorted by urgency (soonest first).
        """
        heap = MinHeap()
        
        # Group history by bin_id and sort by timestamp
        bin_history = {}
        for h in history:
            bid = h.get('bin_id')
            if bid not in bin_history:
                bin_history[bid] = []
            bin_history[bid].append(h)
        
        # Sort each bin's history by timestamp
        for bid in bin_history:
            bin_history[bid].sort(key=lambda x: x.get('timestamp', ''))

        for b in bins:
            if b.fill_level >= 100:
                # Already overflowing
                heap.push(0, b)
                continue
            
            if b.fill_level == 0:
                # Empty bin - will take longest to overflow
                # Calculate based on fill rate
                rate = self._calculate_fill_rate(b, bin_history.get(b.id, []))
                if rate > 0:
                    hours_left = 100 / rate  # Time to fill from 0% to 100%
                else:
                    hours_left = 9999
                heap.push(hours_left, b)
                continue

            # Calculate fill rate from historical data
            rate = self._calculate_fill_rate(b, bin_history.get(b.id, []))
            
            # Calculate hours until overflow
            remaining_capacity = 100 - b.fill_level
            if rate > 0:
                hours_left = remaining_capacity / rate
            else:
                hours_left = 9999  # Never overflows

            heap.push(hours_left, b)

        # Return sorted list (min-heap ensures soonest overflow first)
        return heap.to_list()
    
    def _calculate_fill_rate(self, bin_obj, bin_events):
        """
        Calculate fill rate (% per hour) from historical data.
        Analyzes collection events to determine average fill rate.
        """
        if len(bin_events) < 2:
            # Insufficient data - use waste type heuristic
            return self._get_heuristic_rate(bin_obj.waste_type)
        
        # Calculate fill rates between collection events
        fill_rates = []
        
        for i in range(len(bin_events) - 1):
            current = bin_events[i]
            next_event = bin_events[i + 1]
            
            # Only calculate rate if we have prev_fill data (from dispatch/collection)
            if 'prev_fill' in next_event and current.get('status') == 'Collected':
                # After collection, bin was at 0%
                # Before next collection, bin was at prev_fill%
                fill_amount = next_event.get('prev_fill', 0)
                
                # Calculate time difference
                try:
                    t1 = datetime.datetime.strptime(current.get('timestamp'), "%Y-%m-%d %H:%M:%S")
                    t2 = datetime.datetime.strptime(next_event.get('timestamp'), "%Y-%m-%d %H:%M:%S")
                    hours_diff = (t2 - t1).total_seconds() / 3600
                    
                    if hours_diff > 0:
                        rate = fill_amount / hours_diff
                        fill_rates.append(rate)
                except:
                    continue
        
        if fill_rates:
            # Return average fill rate from historical data
            avg_rate = sum(fill_rates) / len(fill_rates)
            return max(0.1, avg_rate)  # Minimum 0.1% per hour
        
        # Fallback to heuristic if no valid rates calculated
        return self._get_heuristic_rate(bin_obj.waste_type)
    
    def _get_heuristic_rate(self, waste_type):
        """
        Fallback heuristic rates when historical data is insufficient.
        Based on typical waste accumulation patterns.
        """
        heuristic_rates = {
            "Organic": 2.5,      # Fills fastest (daily food waste)
            "Household": 1.5,    # Moderate (general household waste)
            "Recyclable": 1.0,   # Slower (periodic recycling)
            "Industrial": 0.5    # Slowest (bulk industrial waste)
        }
        return heuristic_rates.get(waste_type, 1.0)
