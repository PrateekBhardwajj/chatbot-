import os
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from datetime import timedelta
from functools import wraps
    
# Load environment variables (if needed)
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure session management
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'supersecretkey')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
Session(app)
jwt = JWTManager(app)

# Initialize OpenAI Chat model
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)

# Define prompt templates for each persona
developer_prompt_template = os.getenv("DEVELOPER_PROMPT")

hr_prompt_template = os.getenv("HR_PROMPT")

business_coach_prompt_template = os.getenv("BUSINESS_PROMPT")

# Define prompt templates using the loaded strings
developer_prompt = PromptTemplate(input_variables=["history", "input"], template=developer_prompt_template)
hr_prompt = PromptTemplate(input_variables=["history", "input"], template=hr_prompt_template)
business_coach_prompt = PromptTemplate(input_variables=["history", "input"], template=business_coach_prompt_template)

# Defining a function to create conversation chains
def create_conversation_chain(prompt):
    return ConversationChain(llm=llm, prompt=prompt, memory=ConversationBufferMemory())

# Initialize conversation chains for each persona
conversation_chains = {
    "developer": create_conversation_chain(developer_prompt),
    "hr": create_conversation_chain(hr_prompt),
    "business_coach": create_conversation_chain(business_coach_prompt)
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    # Here you should add logic to verify username and password # middleware 
    if username != 'user' or password != 'password':
        return jsonify({"msg": "Bad username or password"}), 401

    # Create a new token with the user id inside
    access_token = create_access_token(identity=username)
    session['username'] = username
    session['token'] = access_token
    return jsonify(access_token=access_token), 200
#Middleware to check if the user is logged in and has a valid token
def token_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"msg": "Invalid token or token expired"}), 401
        return f(*args, **kwargs)
    return decorated

def validate_request(data):
    print(data)
    # Check if 'message' is present and is a string
    if 'message' not in data or not isinstance(data['message'], str):
        return False, "Invalid or missing 'message' field"
    
    if 'message' not in data or not data['message'].strip():
        return False, "The 'message' field is required and cannot be empty."

    # Check if 'persona' is present and is a string
    if 'persona' not in data or not isinstance(data['persona'], str):
        return False, "Invalid or missing 'persona' field"

    # Check if 'persona' is one of the allowed values
    allowed_personas = {'hr', 'developer', 'business_coach'}
    if data['persona'] not in allowed_personas:
        return False, "Invalid 'persona' value"

    return True, None


@app.route('/chat', methods=['POST'])
@token_required
def chat():
    try:
        data = request.json

        # Validate the request data
        is_valid, error_message = validate_request(data)
        
        print("IS Valid", is_valid)
        
        print("error", error_message)
        
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Proceed with processing
        user_input = data["message"]
        persona = data["persona"]
        
        # Retrieve the appropriate conversation chain
        conversation_chain = conversation_chains[persona]
        
        # Generate response
        response = conversation_chain.run(input=user_input)
        
        # Check if the response is empty or not informative
        if not response.strip():
            return jsonify({"response": "I don't know"}), 200

        return jsonify({"response": response}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    