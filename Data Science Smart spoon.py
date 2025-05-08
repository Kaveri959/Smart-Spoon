import random
import numpy as np
import pandas as pd
from IPython.display import display, Javascript, Image
from google.colab import files
from google.colab.output import eval_js # type: ignore
from base64 import b64decode
import time
from PIL import Image as PILImage
import io

# Enhanced food database with color profiles
FOOD_DATABASE = {
    "biryani": {
        "ingredients": ["rice", "chicken", "spices", "yogurt", "saffron"],
        "salt_content": "medium",
        "spice_level": "high",
        "color_profile": [(180, 150, 50), (200, 120, 30)],
        "default_taste": "balanced"
    },
    "dosa": {
        "ingredients": ["rice flour", "lentils", "salt", "oil"],
        "salt_content": "low",
        "spice_level": "medium",
        "color_profile": [(220, 200, 150), (240, 220, 180)],
        "default_taste": "mild"
    },
    "pizza": {
        "ingredients": ["flour", "cheese", "tomato sauce", "toppings"],
        "salt_content": "high",
        "spice_level": "low",
        "color_profile": [(180, 50, 50), (220, 80, 80)],
        "default_taste": "savory"
    },
    "dal tadka": {
        "ingredients": ["lentils", "turmeric", "cumin", "garlic"],
        "salt_content": "medium",
        "spice_level": "medium",
        "color_profile": [(200, 180, 80), (220, 200, 100)],
        "default_taste": "earthy"
    },
    "idli": {
        "ingredients": ["rice", "urad dal", "salt"],
        "salt_content": "low",
        "spice_level": "low",
        "color_profile": [(240, 240, 240), (255, 255, 255)],
        "default_taste": "neutral"
    }
}

# Global variable to store uploaded data
uploaded_data = None
user_profile = {}

def upload_excel():
    """Handle Excel/CSV file upload and analysis"""
    uploaded = files.upload()
    for filename in uploaded.keys():
        if filename.endswith('.xlsx'):
            df = pd.read_excel(filename)
        elif filename.endswith('.csv'):
            df = pd.read_csv(filename)
        else:
            print(f"Unsupported file format: {filename}")
            continue

        print(f"\nSuccessfully uploaded {filename}")
        print("\n=== Excel Data Analysis ===")

        # Basic analysis
        if 'Age' in df.columns:
            print(f"\nAverage age of users: {df['Age'].mean():.1f} years")

        if 'Gender' in df.columns:
            print("\nGender distribution:")
            print(df['Gender'].value_counts())

        if 'Medical Condition' in df.columns:
            print("\nMedical conditions:")
            print(df['Medical Condition'].value_counts())

        if 'Restaurant Frequency' in df.columns:
            print("\nRestaurant visit frequency:")
            print(df['Restaurant Frequency'].value_counts())

        return df
    return None

def get_user_profile():
    """Collect user demographic information"""
    print("\n=== User Profile ===")
    user_profile['age'] = input("Please enter your age: ")
    user_profile['gender'] = input("Gender (Male/Female/Other): ").capitalize()
    user_profile['frequency'] = input("How often do you visit restaurants? (Daily/Weekly/Monthly/Rarely): ").capitalize()
    user_profile['medical'] = input("Any medical conditions? (Hypertension/Kidney Disease/None): ").capitalize()
    return user_profile

def get_dietary_recommendations(food_data):
    """Generate dietary recommendations based on user profile"""
    print("\n=== Dietary Recommendations ===")

    # Salt recommendation based on medical condition
    if user_profile.get('medical') in ['Hypertension', 'Kidney disease']:
        print("Recommended salt: 1/4 tsp (due to medical condition)")
    elif food_data['salt_content'] == 'high':
        print("Recommended salt: 1/2 tsp (this dish is naturally high in salt)")
    else:
        print("Recommended salt: 1 tsp (standard recommendation)")

    # Additional recommendations
    if user_profile.get('frequency') in ['Daily', 'Weekly']:
        print("Note: Frequent restaurant visits suggest monitoring sodium intake")

    if user_profile.get('age') and int(user_profile['age']) > 60:
        print("Senior recommendation: Consider reduced spice stimulation")

def food_analysis_workflow():
    """Main food analysis workflow"""
    print("\n=== Food Analysis Options ===")
    print("1. Take photo with camera")
    print("2. Upload image file")
    choice = input("Select option (1-2): ")

    if choice == "1":
        filename = take_photo()
    elif choice == "2":
        filename = upload_image()
        if not filename:
            print("No valid image file found")
            return
    else:
        print("Invalid choice")
        return

    print("\nFood image ready!")
    display(Image(filename))

    # Step 1: Get user profile
    get_user_profile()

    # Step 2: Analyze food
    print("\nAnalyzing your food...")
    time.sleep(2)  # Simulate processing time
    food_data, food_name = analyze_food(filename)

    print(f"\nDetected: {food_name.title()}")
    print(f"Main Ingredients: {', '.join(food_data['ingredients'])}")
    print(f"Typical Salt Content: {food_data['salt_content']}")
    print(f"Spice Level: {food_data['spice_level']}")

    # Step 3: Show dietary recommendations
    get_dietary_recommendations(food_data)

    # Step 4: Get user feedback
    while True:
        feedback = input("\nHow does your food taste? (ok/need more taste/need less taste/other): ").lower()

        # Step 5: Provide suggestions
        suggestions = suggest_improvements(food_data, feedback)
        print("\nSmart Spoon Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")

        # Step 6: Check satisfaction
        satisfied = input("\nAre you satisfied now? (yes/no): ").lower()
        if satisfied == 'yes':
            break

    # Step 7: Conclusion
    print("\nThank you for using Smart Spoon!")
    print("Enjoy your perfectly flavored meal!")


def take_photo(filename='photo.jpg', quality=0.8):
    """Capture image from camera"""
    js = Javascript('''
    async function takePhoto(quality) {
        const div = document.createElement('div');
        const video = document.createElement('video');
        video.style.display = 'block';
        const stream = await navigator.mediaDevices.getUserMedia({video: true});

        document.body.appendChild(div);
        div.appendChild(video);
        video.srcObject = stream;
        await video.play();

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        const img_data = canvas.toDataURL('image/jpeg', quality);
        stream.getVideoTracks()[0].stop();
        div.remove();
        return img_data;
    }
    ''')

    display(js)
    data = eval_js('takePhoto({})'.format(quality))
    binary = b64decode(data.split(',')[1])
    with open(filename, 'wb') as f:
        f.write(binary)
    return filename

def upload_image():
    """Handle image file upload"""
    uploaded = files.upload()
    for filename in uploaded.keys():
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return filename
    return None

def get_image_color_profile(image_path):
    """Analyze the dominant colors in the image"""
    img = PILImage.open(image_path)
    img = img.resize((100, 100))  # Resize for faster processing
    pixels = np.array(img)

    # Calculate average color
    avg_color = np.mean(pixels, axis=(0, 1))
    return avg_color

def analyze_food(image_path):
    """Improved food analysis based on color profile"""
    try:
        # Get the color profile of the captured image
        image_color = get_image_color_profile(image_path)

        # Find the best matching food based on color
        best_match = None
        min_distance = float('inf')

        for food_name, food_data in FOOD_DATABASE.items():
            for color_range in food_data["color_profile"]:
                # Calculate color distance
                distance = np.linalg.norm(image_color - np.array(color_range))
                if distance < min_distance:
                    min_distance = distance
                    best_match = (food_name, food_data)

        return best_match[1], best_match[0]
    except:
        # Fallback to random selection if analysis fails
        food_item = random.choice(list(FOOD_DATABASE.keys()))
        return FOOD_DATABASE[food_item], food_item

def suggest_improvements(food_data, feedback):
    """Generate improvement suggestions"""
    suggestions = []

    if "more taste" in feedback.lower():
        if food_data['salt_content'] == 'low':
            suggestions.append("Increase salt stimulation by 20%")
        if food_data['spice_level'] == 'low':
            suggestions.append("Enhance spice perception")
        suggestions.append("Boost umami flavor profile")
        suggestions.append("Add mild electric stimulation for richer taste")

    elif "less taste" in feedback.lower():
        if food_data['salt_content'] in ['medium', 'high']:
            suggestions.append("Reduce salt stimulation by 15%")
        if food_data['spice_level'] in ['medium', 'high']:
            suggestions.append("Decrease spice perception")
        suggestions.append("Balance flavor profile")
        suggestions.append("Reduce electric stimulation for milder taste")

    else:  # other modifications
        suggestions.append("Adjust flavor balance based on your preference")
        suggestions.append("Optimize taste stimulation levels")
        suggestions.append("Try alternating between different stimulation patterns")

    return suggestions

def smart_spoon_system():
    """Main system interface"""
    print("=== Smart Spoon Food Advisor ===")

    # First ask to upload Excel/CSV
    print("\nStep 1: Upload your Excel/CSV file (optional)")
    upload_choice = input("Would you like to upload an Excel/CSV file? (yes/no): ").lower()

    if upload_choice == 'yes':
        global uploaded_data
        uploaded_data = upload_excel()

    # Then proceed to food analysis
    while True:
        print("\nMain Menu:")
        print("1. Analyze food")
        print("2. Exit")
        choice = input("Select option (1-2): ")

        if choice == "1":
            food_analysis_workflow()
        elif choice == "2":
            print("\nThank you for using Smart Spoon!")
            break
        else:
            print("Invalid choice, please try again")

# Run the system
smart_spoon_system()