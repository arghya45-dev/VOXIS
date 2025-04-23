from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.http import JsonResponse
from dotenv import load_dotenv
import os
from groq import Groq  # Make sure `groq` is installed via pip
from django.views.decorators.csrf import csrf_exempt
from .forms import ContactForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout

from django.contrib.auth import update_session_auth_hash

from django.conf import settings
# from django.shortcuts import renderz
from gtts import gTTS



# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'home.html', {'form': ContactForm(), 'success': True})
    else:
        form = ContactForm()
    return render(request, 'home.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('dashboard')
    else:
        initial_data = {'username':'', 'password1':'','password2':""}
        form = UserCreationForm(initial=initial_data)
    return render(request, 'register.html',{'form':form})


def dashboard_view(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('home')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('home')
    else:
        initial_data = {'username':'', 'password':''}
        form = AuthenticationForm(initial=initial_data)
    return render(request, 'login.html',{'form':form})

@login_required
def edit_profile(request):
        if request.method == 'POST':
            user = request.user
            name = request.POST['name']
            username = request.POST['username']
            email = request.POST['email']
            
            if User.objects.exclude(pk=user.pk).filter(username=username).exists():
                messages.error(request, "Username is already taken.")
                return redirect('edit_profile')
    
            if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                messages.error(request, "Email is already registered.")
                return redirect('edit_profile')
    
            user.first_name = name
            user.username = username
            user.email = email
            user.save()
    
            # Password change handling
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
    
            if current_password and new_password and confirm_password:
                if user.check_password(current_password):
                    if new_password == confirm_password:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)  # Keep user logged in after password change
                        messages.success(request, "Profile updated successfully!")
                        return redirect('dashboard')
                    else:
                        messages.error(request, "New passwords do not match.")
                else:
                    messages.error(request, "Incorrect current password.")
    
            messages.success(request, "Profile updated successfully!")
            return redirect('dashboard')
    
        return render(request, 'edit_profile.html')



def assist(request):
    return render(request, 'assist.html')


# Handles the voice/chat prompt
def ask_groq(request):
    if request.method == 'POST':
        prompt = request.POST.get('message', '')

        # Initialize chat history if not present
        if 'chat_history' not in request.session:
            request.session['chat_history'] = []

        # Add user's message to chat history
        request.session['chat_history'].append({'role': 'user', 'content': prompt})

        try:
            # Send entire history to Groq
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=request.session['chat_history']
            )

            reply = response.choices[0].message.content

            # Add assistant's reply to history
            request.session['chat_history'].append({'role': 'assistant', 'content': reply})
            request.session.modified = True  # Mark session as changed

            return JsonResponse({'response': reply, 'history': request.session['chat_history']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Assuming you're storing the conversation in the session
def clear_chat(request):
    # Clear the chat history stored in the session
    request.session['chat_history'] = []  # Clears the session history
    return JsonResponse({'status': 'success'})


def text_to_speech(request):
    audio_file_url = None  
    user_text = ""

    if request.method == "POST":
        user_text = request.POST.get("text", "")

        if user_text.strip():  # Ensure text is not empty
            # Define correct media path
            audio_file_path = os.path.join(settings.MEDIA_ROOT, "speech.mp3")

            # Generate speech
            tts = gTTS(text=user_text, lang="en")
            tts.save(audio_file_path)  # Save to correct location

            # Generate file URL
            audio_file_url = settings.MEDIA_URL + "speech.mp3"

    return render(request, "text_to_speech.html", {"audio_file_url": audio_file_url, "user_text": user_text})

