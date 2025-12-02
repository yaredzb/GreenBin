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
    
    def _parse_timestamp(self, ts_str):
        """Helper to parse timestamp string (ISO or old format)."""
        dt = None
        try:
            dt = datetime.datetime.fromisoformat(ts_str)
        except ValueError:
            try:
                dt = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        
        # Ensure timezone awareness (assume UTC if naive)
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        
        return dt

    def _calculate_fill_rate(self, bin_obj, bin_events):
        """
        Calculate fill rate (% per hour) from historical data.
        Analyzes collection events to determine average fill rate.
        """
        if len(bin_events) < 2:
            # Insufficient data - use waste type heuristic
            return self._get_heuristic_rate(bin_obj.waste_type)
        
        # Method 1: Calculate fill rates between collection events
        fill_rates_from_collections = []
        
        # Find all collection events
        collection_events = [e for e in bin_events if e.get('status') == 'Collected']
        
        for i in range(len(collection_events) - 1):
            current_collection = collection_events[i]
            next_collection = collection_events[i + 1]
            
            # The fill level before next collection tells us how much accumulated
            if 'prev_fill' in next_collection:
                fill_amount = next_collection.get('prev_fill', 0)
                
                # Calculate time difference between collections
                t1 = self._parse_timestamp(current_collection.get('timestamp'))
                t2 = self._parse_timestamp(next_collection.get('timestamp'))
                
                if t1 and t2:
                    hours_diff = (t2 - t1).total_seconds() / 3600
                    if hours_diff > 0:
                        rate = fill_amount / hours_diff
                        fill_rates_from_collections.append(rate)
        
        # Method 2: Calculate rate from any consecutive events with fill level data
        fill_rates_from_status = []
        
        for i in range(len(bin_events) - 1):
            current = bin_events[i]
            next_event = bin_events[i + 1]
            
            # If we have fill levels for both events
            current_fill = current.get('fill_level')
            next_fill = next_event.get('fill_level') or next_event.get('prev_fill')
            
            if current_fill is not None and next_fill is not None:
                # Skip if it's a collection (sudden drop to 0)
                if current.get('status') == 'Collected':
                    continue
                    
                fill_change = next_fill - current_fill
                
                # Only consider positive changes (bins filling up, not being emptied)
                if fill_change > 0:
                    t1 = self._parse_timestamp(current.get('timestamp'))
                    t2 = self._parse_timestamp(next_event.get('timestamp'))
                    
                    if t1 and t2:
                        hours_diff = (t2 - t1).total_seconds() / 3600
                        if hours_diff > 0:
                            rate = fill_change / hours_diff
                            fill_rates_from_status.append(rate)
        
        # Combine all valid rates
        all_rates = fill_rates_from_collections + fill_rates_from_status
        
        if all_rates:
            # Return average fill rate from historical data
            avg_rate = sum(all_rates) / len(all_rates)
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
