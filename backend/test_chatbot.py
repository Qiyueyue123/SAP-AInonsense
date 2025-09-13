import json
from agents.career_coach import get_chatbot_response

def run_chat_session():
    """
    Runs an interactive command-line chat session to test the career coach agent.
    """
    print("--- Career Coach Chatbot Test ---")
    print("Type 'exit' to end the session.")
    print("-" * 30)

    # 1. MOCK USER DATA
    # This simulates the data that would normally be fetched from Firestore.
    # You can change these values to test different scenarios.
    mock_user_profile = {
        "skillScores": {
            "Code Optimization": 12.5,
            "Database Management": 9.0,
            "Data Analysis": 15.0,
            "UI/UX Design": 5.0,
            "Automation/Scripting": 11.0,
            "Communication": 18.0,
            "Problem Solving": 16.0,
            "Client Management": 14.0,
            "Team Leadership": 8.0,
            "Presentation Skills": 17.0,
        },
        "targetVector": {
            "Code Optimization": 15,
            "Team Leadership": 12,
        },
         "qualitativeFeedback": {
            "strengths": "Excels in communication and data-driven problem solving.",
            "weaknesses": "Lacks experience in UI/UX design and team leadership."
        }
    }

    # 2. CHAT HISTORY
    # This list will store the conversation, just like the frontend would.
    chat_history = []

    # 3. INTERACTIVE LOOP
    while True:
        user_message = input("\nYou: ")
        if user_message.lower() == 'exit':
            print("Ending chat session.")
            break

        # Append user message to history
        chat_history.append({"role": "user", "content": user_message})

        # Call the actual career coach agent function
        print("\nCoach is thinking...")
        ai_response = get_chatbot_response(user_message, chat_history, mock_user_profile)

        # Add a check to ensure the response is a valid dictionary
        if not isinstance(ai_response, dict):
            print("\nCoach: [ERROR] The AI agent returned an invalid response. Please check the agent's code.")
            # Add a placeholder to history to avoid breaking the loop's logic
            chat_history.append({"role": "assistant", "content": "[AGENT ERROR]"})
            continue

        # Safely get the content and print the AI's response
        response_content = ai_response.get('content', "Sorry, I couldn't generate a response.")
        print(f"\nCoach: {response_content}")

        # Append the valid AI response to history
        chat_history.append(ai_response)
        
        # If the AI used a tool that updated the profile, we could reflect it here
        # For example, if it updated the targetVector, we could print the change.
        # This is a more advanced step for testing.


if __name__ == '__main__':
    run_chat_session()

