import groq

groq_api_key = "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"

client = groq.Groq(api_key=groq_api_key)

def detect_spam(message):
    prompt = f"""
You are a spam detection AI. Read the message and classify it as "Spam" or "Not Spam". Then explain the reason in one or two sentences.

Message: "{message}"

Classification:"""

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # or another supported Groq model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that detects spam and explains its reasoning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100,  # Increased for full explanation
        )

        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    while True:
        user_input = input("Enter a message to check (or type 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        result = detect_spam(user_input)
        print(f"\n{result}\n")