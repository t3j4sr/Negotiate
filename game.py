import random
import re
import math
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Simple auto driver game with Bangalore area knowledge
class BangaloreAutoGame:
    def __init__(self):
        # Response tracking to prevent repetition
        self.used_responses = {
            'ask_destination': [],
            'unknown_place': [],
            'price_high': [],
            'price_medium': [],
            'price_low': [],
            'too_low': [],
            'agreement': []
        }
        
        # Define Bangalore areas with coordinates (approximate lat/long positioning)
        # Format: [area_name, [x, y]] where x,y are relative positions
        self.bangalore_areas = {
            # South Bangalore
            "jayanagar": [1, -5],
            "jp nagar": [0, -6],
            "banashankari": [-1, -7],
            "uttarahalli": [-2, -8],
            "kanakapura": [-3, -12],
            "bannerghatta": [2, -9],
            
            # Central
            "majestic": [0, 0],
            "mg road": [2, 0],
            "brigade road": [2, -1],
            "richmond town": [1, -2],
            "shivajinagar": [1, 1],
            "cubbon park": [2, 0],
            "ulsoor": [3, 1],
            
            # East
            "indiranagar": [5, 0],
            "domlur": [4, -1],
            "marathahalli": [8, -1],
            "whitefield": [12, -2],
            
            # North
            "hebbal": [0, 5],
            "yelahanka": [0, 10],
            "devanahalli": [1, 15],
            "airport": [2, 18],
            
            # West
            "rajajinagar": [-3, 2],
            "malleswaram": [-2, 1],
            "yeshwanthpur": [-3, 3],
            "peenya": [-4, 5],
            
            # South-East
            "koramangala": [4, -3],
            "btm layout": [3, -4],
            "hsr layout": [5, -5],
            "electronic city": [7, -10],
            "silk board": [5, -6],
            
            # South-West
            "vijayanagar": [-4, -3],
            "mysore road": [-5, -5],
            "kengeri": [-7, -7],
            "rajarajeshwari nagar": [-6, -6]
        }
        
        # Current location parameters
        self.current_location = "majestic"  # Default starting point
        self.destination = None
        self.distance = None
        self.base_price = None
        self.min_price = None
        self.current_price = None
        
        # Game state and conditions
        self.time = datetime.now().hour
        self.traffic_level = random.choice(['low', 'medium', 'high', 'very_high'])
        self.weather = random.choice(['clear', 'rainy', 'heavy_rain'])
        self.driver_mood = random.choice(['good', 'neutral', 'bad'])
        
        # Constants for price calculation
        self.base_fare = 40  # Increased minimum fare
        self.rate_per_km = 18  # Increased rate per km
        self.night_multiplier = 1.5 if self.time < 6 or self.time >= 22 else 1.0
        self.traffic_multiplier = {
            'low': 1.0,
            'medium': 1.2,
            'high': 1.4,
            'very_high': 1.6
        }[self.traffic_level]
        self.weather_multiplier = {
            'clear': 1.0,
            'rainy': 1.3,
            'heavy_rain': 1.5
        }[self.weather]
        self.haggling_factor = 1.6  # Higher initial price for harder bargaining
        
        # Driver responses based on mood and conditions
        self.responses = {
            "ask_destination": [
                "Kahan jana hai bhai?",
                "Where to?",
                "Jana kahan hai? Jaldi bolo, time nahi hai.",
                "Tell me your destination; fare will run on meter.",
                "Kahan chaloge? {weather} mein extra lagega.",
                "Bolo bhai, {traffic} traffic hai aaj."
            ],
            "unknown_place": [
                "Woh kahan hai bhai? Koi landmark bolo.",
                "Yeh area nahi jaanta, koi aur batao.",
                "Naya area hai kya? Google Maps dikhao.",
                "Yeh kahan hai? MG Road, Indiranagar jaisa batao.",
                "Area ka naam theek se bolo, samajh nahi aa raha."
            ],
            "price_high": [
                "₹{price}, {traffic} traffic hai.",
                "₹{price} lagega, {weather} mein extra.",
                "Raat ko ₹{price} se kam nahi.",
                "Itna traffic hai, ₹{price} minimum.",
                "Petrol ka rate pata hai? ₹{price} final.",
                "CNG ka rate badh gaya, ₹{price} se start."
            ],
            "price_medium": [
                "Accha ₹{price}, lekin {condition}.",
                "₹{price} final, {traffic} traffic hai.",
                "₹{price} se kam nahi, {weather} chal raha hai.",
                "Bhai ₹{price}, reasonable rate hai.",
                "Meter se bhi ₹{price} hi aayega."
            ],
            "price_low": [
                "Nahi bhai, ₹{price}. {condition}",
                "Petrol mehenga hai, ₹{price} final.",
                "₹{price} se kam impossible, {traffic} traffic hai.",
                "Itna kam? ₹{price}, woh bhi {weather} mein.",
                "Bhai reasonable bolo, ₹{price} last."
            ],
            "too_low": [
                "Arrey bhai, mazak mat karo! ₹{price}, {condition}",
                "Utne mein toh petrol bhi nahi aayega. ₹{price} minimum.",
                "Itna kam? Chalte raho bhai. ₹{price} se kam nahi.",
                "Aaj kal ka rate pata hai? ₹{price} normal hai.",
                "Dusra auto dekho phir, mere ko ₹{price} chahiye."
            ],
            "agreement": [
                "Chalo baitho, {weather} mein jaldi chalenge.",
                "Theek hai, par {traffic} traffic hai.",
                "Ok done, lekin route mere hisaab se.",
                "Haan aa jao, meter se dikha dunga same rate.",
                "Chalo chalo, time waste mat karo."
            ],
            "close_distance": [
                "Itna paas? Phir bhi ₹{price}, {condition}",
                "Short distance ₹{price}, {traffic} traffic hai.",
                "Minimum ₹{price}, {weather} mein extra.",
                "Meter se ₹{price} hi aayega, check kar lo.",
                "Paas hai par one-way hai, ₹{price} lagega."
            ],
            "far_distance": [
                "Itna door? ₹{price}, woh bhi {condition}",
                "Full Bangalore cross karna hai! ₹{price} kam hai.",
                "Itna door {weather} mein ₹{price} reasonable hai.",
                "Long route hai, {traffic} traffic mein ₹{price}.",
                "Airport rate hai yeh, ₹{price} normal hai."
            ]
        }
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def find_closest_area(self, query):
        """Find closest matching area from input"""
        query = query.lower()
        # Direct match
        if query in self.bangalore_areas:
            return query
            
        # Check for partial matches
        for area in self.bangalore_areas:
            if query in area or area in query:
                return area
                
        # No match found
        return None
        
    def calculate_price(self, distance):
        """Calculate fare based on distance and conditions"""
        # Base calculation
        raw_price = self.base_fare + (distance * self.rate_per_km)
        
        # Apply condition multipliers
        raw_price *= self.night_multiplier  # Night charges
        raw_price *= self.traffic_multiplier  # Traffic conditions
        raw_price *= self.weather_multiplier  # Weather conditions
        
        # Apply mood-based variation (±10%)
        mood_multiplier = {
            'good': 0.9,
            'neutral': 1.0,
            'bad': 1.1
        }[self.driver_mood]
        raw_price *= mood_multiplier
        
        # Apply haggling factor (drivers quote higher initially)
        quoted_price = raw_price * self.haggling_factor
        
        # Round to nearest 10 for quoted price (auto drivers always quote in round numbers)
        quoted_price = round(quoted_price / 10) * 10
        
        # Ensure quoted price ends in 0 or 5
        if quoted_price % 10 != 0 and quoted_price % 5 != 0:
            quoted_price = round(quoted_price / 5) * 5
        
        # Round minimum price to nearest 10 internally
        min_price = max(self.base_fare, round(raw_price / 10) * 10)
        
        return int(quoted_price), int(min_price)
    
    def start(self):
        """Start the game"""
        print("🛺 You're negotiating with an auto driver in Bangalore!")
        print("🎯 Ask to go to areas like MG Road, Indiranagar, Koramangala, etc.")
        print("🗺️ The driver is currently at " + self.current_location.title())
        print("🔍 Type 'exit' to end the conversation\n")
        
        # First driver response
        response = self.get_unique_response('ask_destination')
        # Safely format the response with all possible placeholders
        response = self.safe_format(response, weather=self.weather, traffic=self.traffic_level)
        print(f"AI: {response}")
        
        # Main conversation loop
        conversation_active = True
        while conversation_active:
            user_input = input("You: ").strip().lower()
            
            # Check for exit command
            if user_input in ["exit", "quit", "bye"]:
                print("Exiting conversation...")
                return False
            
            # Process the conversation
            if not self.destination:
                self.process_destination(user_input)
            else:
                result = self.process_negotiation(user_input)
                if result == "done":
                    conversation_active = False
        
        # Evaluate the negotiation
        self.evaluate_negotiation()
        return True
            
    def process_destination(self, user_input):
        """Process user input to find destination"""
        # Try to extract destination from user input
        closest_area = None
        
        # Check each area name
        for area in self.bangalore_areas:
            if area in user_input:
                closest_area = area
                break
                
        # If no direct match, try to find through partial matching
        if not closest_area:
            words = user_input.split()
            for word in words:
                if len(word) > 3:  # Avoid short words
                    closest_area = self.find_closest_area(word)
                    if closest_area:
                        break
            
        if closest_area:
            self.destination = closest_area
            
            # Calculate distance
            start_coords = self.bangalore_areas[self.current_location]
            dest_coords = self.bangalore_areas[self.destination]
            self.distance = self.calculate_distance(start_coords, dest_coords)
            
            # Calculate prices
            self.base_price, self.min_price = self.calculate_price(self.distance)
            self.current_price = self.base_price
            
            # Choose response based on distance
            if self.distance < 3:
                response = self.get_unique_response('close_distance')
                response = self.safe_format(response, price=self.current_price)
            elif self.distance > 10:
                response = self.get_unique_response('far_distance')
                response = self.safe_format(response, price=self.current_price)
            else:
                response = self.get_unique_response('price_high')
                response = self.safe_format(response, price=self.current_price)
                
            print(f"AI: {response}")
        else:
            # Unknown destination
            print(f"AI: {self.get_unique_response('unknown_place')}")
    
    def process_negotiation(self, user_input):
        """Process negotiation after destination is set"""
        # Extract price from user input
        price_match = re.search(r'(\d+)', user_input)
        user_price = int(price_match.group(1)) if price_match else None
        
        # Get current conditions
        condition = f"traffic {self.traffic_level}" if random.random() < 0.5 else f"weather {self.weather}"
        
        # Check for disagreement words first
        disagreement_words = ["nahi", "no", "not", "illogical", "expensive", "costly", "zyada", "bahut", "too much", "cab", "uber", "ola"]
        disagreement_pattern = r'\b(?:' + '|'.join([re.escape(w) for w in disagreement_words]) + r')\b'
        
        # Check for agreement words
        agreement_words = ["ok", "okay", "theek", "thik", "thike", "done", "fine", 
                         "agree", "chalo", "let's go", "deal", "chalega"]
        
        # Word-boundary match to avoid partial matches (e.g., 'only')
        agreement_pattern = r'\b(?:' + '|'.join([re.escape(w) for w in agreement_words]) + r')\b'
        
        # If there's a disagreement word, don't consider it an agreement
        if re.search(disagreement_pattern, user_input, flags=re.IGNORECASE):
            # User is disagreeing with the price
            # Larger reduction for explicit disagreement (in multiples of 10)
            reduction = random.randint(2, 5) * 10
            self.current_price = max(self.min_price, self.current_price - reduction)
            # Round to nearest 10 or 5
            self.current_price = round(self.current_price / 10) * 10
            
            # Get a non-repetitive response
            response = self.get_unique_response('price_medium')
            # Safely format with all possible placeholders
            response = self.safe_format(response, 
                                        price=self.current_price,
                                        condition=condition,
                                        traffic=self.traffic_level,
                                        weather=self.weather)
            print(f"AI: {response}")
            return "continue"
        
        # No disagreement words found, check for agreement
        elif re.search(agreement_pattern, user_input, flags=re.IGNORECASE):
            if user_price:
                if user_price >= self.min_price:
                    # User agreed to a specific price that's acceptable
                    self.current_price = user_price
                    response = self.get_unique_response('agreement')
                    # Safely format with all possible placeholders
                    response = self.safe_format(response, weather=self.weather, traffic=self.traffic_level)
                    print(f"AI: {response}")
                    return "done"
                else:
                    # Too low price with agreement word
                    response = self.get_unique_response('too_low')
                    # Safely format with all possible placeholders
                    response = self.safe_format(response, 
                                              price=max(self.min_price, self.current_price - 10),
                                              condition=condition)
                    self.current_price = max(self.min_price, self.current_price - 10)
                    print(f"AI: {response}")
                    return "continue"
            else:
                # User agreed to current price
                response = self.get_unique_response('agreement')
                # Safely format with all possible placeholders
                response = self.safe_format(response, weather=self.weather, traffic=self.traffic_level)
                print(f"AI: {response}")
                return "done"
        
        # Handle user offering a price
        if user_price:
            # User offered way too low (below 85% of minimum)
            if user_price < self.min_price * 0.85:
                response = self.get_unique_response('too_low')
                # Safely format with all possible placeholders
                response = self.safe_format(response, price=self.current_price, condition=condition)
                print(f"AI: {response}")
                return "continue"
                
            price_ratio = user_price / self.base_price
            
            # Track number of negotiation rounds
            if not hasattr(self, 'negotiation_rounds'):
                self.negotiation_rounds = 0
            self.negotiation_rounds += 1
            
            # Driver's acceptance chance based on mood, conditions, and negotiation rounds
            # Start with zero chance on first offer (auto drivers NEVER accept first offer)
            if self.negotiation_rounds <= 1:
                acceptance_chance = 0  # Never accept first offer
            elif self.negotiation_rounds == 2:
                acceptance_chance = 0.1  # Very low chance on second offer
            else:
                acceptance_chance = 0.3  # Base chance after multiple rounds
            
            # Adjust based on driver mood
            if self.driver_mood == 'good':
                acceptance_chance += 0.15
            elif self.driver_mood == 'bad':
                acceptance_chance -= 0.15
                
            # Adjust based on conditions
            if self.traffic_level in ['high', 'very_high']:
                acceptance_chance -= 0.1
            if self.weather in ['rainy', 'heavy_rain']:
                acceptance_chance -= 0.1
            
            # Adjust based on price ratio
            if price_ratio >= 0.95:
                acceptance_chance += 0.2  # Higher chance if close to original price
            elif price_ratio <= 0.7:
                acceptance_chance -= 0.2  # Lower chance if way below original price
            
            # Higher chance of acceptance after many rounds of negotiation
            if self.negotiation_rounds >= 5:
                acceptance_chance += 0.3
            if self.negotiation_rounds >= 8:
                acceptance_chance += 0.2
            
            # Only accept if price is above minimum, after multiple rounds, and probability check passes
            if user_price >= self.min_price and self.negotiation_rounds >= 3 and random.random() < acceptance_chance:
                # Accept the price
                self.current_price = user_price
                response = self.get_unique_response('agreement').format(
                    weather=self.weather,
                    traffic=self.traffic_level
                )
                print(f"AI: {response}")
                return "done"
            else:
                # Counter with a new price
                # Make reductions in multiples of 5 or 10
                if self.driver_mood == 'bad':
                    reduction = random.choice([5, 10, 15])
                elif self.driver_mood == 'good':
                    reduction = random.choice([10, 20, 30])
                else:
                    reduction = random.choice([10, 15, 20])
                    
                # Never go below what the user offered
                if user_price and self.current_price - reduction < user_price:
                    # If user offered more than minimum, accept their price
                    if user_price >= self.min_price:
                        self.current_price = user_price
                    # Otherwise counter with minimum price
                    else:
                        self.current_price = self.min_price
                else:
                    self.current_price = max(self.min_price, self.current_price - reduction)
                    
                # Round to nearest 10 or 5
                self.current_price = round(self.current_price / 5) * 5
                
                if user_price < self.min_price:
                    response = self.get_unique_response('price_low')
                    # Safely format with all possible placeholders
                    response = self.safe_format(response, 
                                              price=self.current_price,
                                              condition=condition,
                                              traffic=self.traffic_level,
                                              weather=self.weather)
                else:
                    response = self.get_unique_response('price_medium')
                    # Safely format with all possible placeholders
                    response = self.safe_format(response, 
                                              price=self.current_price,
                                              condition=condition,
                                              traffic=self.traffic_level,
                                              weather=self.weather)
                print(f"AI: {response}")
        else:
            # General negotiation without specific price
            # Make reductions in multiples of 5 or 10
            if self.driver_mood == 'bad':
                reduction = random.choice([5, 10])
            elif self.driver_mood == 'good':
                reduction = random.choice([10, 15, 20])
            else:
                reduction = random.choice([5, 10, 15])
                
            self.current_price = max(self.min_price, self.current_price - reduction)
            # Round to nearest 5
            self.current_price = round(self.current_price / 5) * 5
            response = self.get_unique_response('price_medium').format(
                price=self.current_price,
                condition=condition,
                traffic=self.traffic_level,
                weather=self.weather
            )
            print(f"AI: {response}")
            
        return "continue"
    
    def evaluate_negotiation(self):
        """Evaluate the negotiation and display results"""
        print("\n📦 Chat ended.")
        print(f"🚕 Destination: {self.destination.title()}")
        print(f"🛣️ Distance: {self.distance:.1f} km (approx)")
        print(f"⏰ Time: {'Night' if self.time < 6 or self.time >= 22 else 'Day'}")
        print(f"🚦 Traffic: {self.traffic_level.title()}")
        print(f"🌤️ Weather: {self.weather.title()}")
        print(f"😊 Driver Mood: {self.driver_mood.title()}")
        print(f"\n💰 Original quote: ₹{self.base_price}")
        print(f"📉 Final agreed price: ₹{self.current_price}")
        print(f"🧾 Driver's minimum: ₹{self.min_price}")
        
        # Calculate score based on conditions
        base_score = ((self.base_price - self.current_price) / (self.base_price - self.min_price)) * 10
        
        # Adjust score based on conditions
        if self.traffic_level in ['high', 'very_high']:
            base_score += 1  # Bonus for negotiating in heavy traffic
        if self.weather in ['rainy', 'heavy_rain']:
            base_score += 1  # Bonus for negotiating in bad weather
        if self.time < 6 or self.time >= 22:
            base_score += 1  # Bonus for night negotiation
        if self.driver_mood == 'bad':
            base_score += 2  # Extra bonus for negotiating with angry driver
        
        score = max(0, min(10, int(base_score)))
        print(f"\n🧠 Negotiation rating: {score}/10")
        
        if score >= 9:
            print("🔥 Legendary negotiator! Even a Bangalore auto driver couldn't resist!")
        elif score >= 7:
            print("💪 Solid bargaining skills! You know your way around autos.")
        elif score >= 5:
            print("👍 Not bad, but there's room for improvement.")
        elif score >= 3:
            print("😅 You got taken for a ride! Try being more assertive.")
        else:
            print("🤦 Rookie mistake! Even tourists bargain better than this!")

    def safe_format(self, text, **kwargs):
        """Safely format a string with only the placeholders it contains"""
        if not text:
            return text
            
        # Find all placeholders in the format {name}
        placeholders = re.findall(r'\{([^\}]+)\}', text)
        
        # Only use the kwargs that are actually in the text
        safe_kwargs = {k: v for k, v in kwargs.items() if k in placeholders}
        
        # Format the string with only the relevant kwargs
        if safe_kwargs:
            try:
                return text.format(**safe_kwargs)
            except KeyError:
                # If there's still a KeyError, return the original text
                return text
        return text
    
    def get_unique_response(self, response_type):
        """Get a response that hasn't been used recently"""
        # Initialize if not already in the tracking dict
        if response_type not in self.used_responses:
            self.used_responses[response_type] = []
            
        available_responses = self.responses.get(response_type, [])
        if not available_responses:
            return "I don't understand."
            
        # If we've used all responses or almost all, reset the tracking
        if len(self.used_responses[response_type]) >= len(available_responses) - 1:
            self.used_responses[response_type] = []
            
        # Filter out recently used responses
        unused_responses = [r for r in available_responses if r not in self.used_responses[response_type]]
        
        # If all have been used, just pick a random one
        if not unused_responses:
            response = random.choice(available_responses)
        else:
            response = random.choice(unused_responses)
            
        # Track this response
        self.used_responses[response_type].append(response)
        
        # Keep track of only the last few responses to allow eventual reuse
        max_history = min(3, len(available_responses) - 1)
        if max_history > 0 and len(self.used_responses[response_type]) > max_history:
            self.used_responses[response_type] = self.used_responses[response_type][-max_history:]
            
        return response

# Run the game
if __name__ == "__main__":
    game = BangaloreAutoGame()
    game.start()