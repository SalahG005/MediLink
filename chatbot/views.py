from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import requests

# Configuration de l'API Gemini avec la nouvelle clé API
GEMINI_API_KEY = 'AIzaSyB7KEOdOJr9y1XvtEAU3ylGAHMyYAzmtHs'
# Essayer plusieurs modèles - gemini-pro est généralement disponible dans le plan gratuit
GEMINI_MODELS = [
    'gemini-pro',  # Généralement disponible dans le plan gratuit
    'gemini-1.5-flash',  # Alternative
    'gemini-2.0-flash',  # Peut avoir un quota limité
]

# Fonction pour lister les modèles disponibles (pour diagnostic)
def list_available_models():
    """Liste les modèles disponibles avec cette clé API"""
    try:
        url = 'https://generativelanguage.googleapis.com/v1beta/models'
        headers = {
            'X-goog-api-key': GEMINI_API_KEY
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            models_data = response.json()
            if 'models' in models_data:
                available_models = []
                for model in models_data['models']:
                    model_name = model.get('name', '').replace('models/', '')
                    # Vérifier si le modèle supporte generateContent
                    if 'generateContent' in model.get('supportedGenerationMethods', []):
                        available_models.append(model_name)
                print(f"Modèles disponibles avec generateContent: {available_models}")
                return available_models
        else:
            print(f"Erreur lors de la récupération des modèles: {response.status_code} - {response.text[:200]}")
    except Exception as e:
        print(f"Erreur lors du listing des modèles: {e}")
    return []

# Lister les modèles disponibles au démarrage (pour diagnostic)
try:
    available = list_available_models()
    if available:
        # Utiliser les modèles disponibles au lieu de la liste fixe
        GEMINI_MODELS = available + GEMINI_MODELS  # Ajouter les modèles disponibles en premier
        GEMINI_MODELS = list(dict.fromkeys(GEMINI_MODELS))  # Supprimer les doublons
        print(f"Modèles à essayer: {GEMINI_MODELS}")
except:
    pass

GEMINI_AVAILABLE = True


@login_required
def chatbot_view(request):
    """Vue principale pour afficher l'interface du chatbot"""
    return render(request, 'chatbot/chatbot.html')


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def chat_api(request):
    """API endpoint pour recevoir les messages et retourner les réponses du chatbot"""
    if not GEMINI_AVAILABLE:
        return JsonResponse({
            'error': 'Le service de chatbot n\'est pas disponible.',
            'status': 'error'
        }, status=503)
    
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Le message ne peut pas être vide'}, status=400)
        
        # Rôle de l'utilisateur
        user_role = getattr(request.user, 'role', 'patient')
        role_context = "patient" if user_role == 'patient' else "médecin professionnel"
        
        # Créer le prompt avec contexte médical
        system_prompt = f"""Tu es un assistant médical intelligent et professionnel qui aide les {role_context}s avec leurs questions médicales.

Instructions importantes:
- Réponds toujours en français
- Sois professionnel, empathique et clair
- Pour les patients: fournis des informations générales et encourage-les à consulter un médecin pour un diagnostic
- Pour les médecins: fournis des informations plus techniques et détaillées
- Ne donne jamais de diagnostic définitif, surtout pour les patients
- Recommande toujours de consulter un professionnel de santé pour les cas sérieux
- Sois concis mais complet dans tes réponses

Question de l'utilisateur: {user_message}"""
        
        # Générer la réponse avec Gemini via l'API REST
        # Essayer plusieurs modèles jusqu'à ce qu'un fonctionne
        last_error = None
        for model_name in GEMINI_MODELS:
            try:
                # Préparer la requête comme dans le curl
                headers = {
                    'Content-Type': 'application/json',
                    'X-goog-api-key': GEMINI_API_KEY
                }
                
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": system_prompt
                                }
                            ]
                        }
                    ]
                }
                
                # URL de l'API pour ce modèle
                api_url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent'
                
                # Faire l'appel API REST
                api_response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
            
                # Vérifier le statut de la réponse
                if api_response.status_code == 200:
                    response_data = api_response.json()
                    
                    # Extraire le texte de la réponse
                    if 'candidates' in response_data and len(response_data['candidates']) > 0:
                        candidate = response_data['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            parts = candidate['content']['parts']
                            if len(parts) > 0 and 'text' in parts[0]:
                                bot_response = parts[0]['text']
                            else:
                                bot_response = "Désolé, je n'ai pas pu générer de réponse. Veuillez reformuler votre question."
                        else:
                            bot_response = "Désolé, je n'ai pas pu générer de réponse. Veuillez reformuler votre question."
                    else:
                        bot_response = "Désolé, je n'ai pas pu générer de réponse. Veuillez reformuler votre question."
                    
                    if not bot_response or bot_response.strip() == '':
                        bot_response = "Désolé, je n'ai pas pu générer de réponse. Veuillez reformuler votre question."
                    
                    print(f"✓ Modèle {model_name} a fonctionné")
                    return JsonResponse({
                        'response': bot_response,
                        'status': 'success'
                    })
                elif api_response.status_code == 429:
                    # Quota dépassé pour ce modèle, essayer le suivant
                    print(f"✗ Modèle {model_name}: quota dépassé, essai du modèle suivant...")
                    last_error = 'Limite de requêtes atteinte. Veuillez réessayer plus tard.'
                    continue
                elif api_response.status_code == 401 or api_response.status_code == 403:
                    return JsonResponse({
                        'error': 'Erreur d\'authentification avec l\'API Gemini. La clé API est peut-être invalide ou expirée.',
                        'status': 'error'
                    }, status=401)
                elif api_response.status_code == 404:
                    # Modèle non disponible, essayer le suivant
                    print(f"✗ Modèle {model_name}: non disponible, essai du modèle suivant...")
                    last_error = f'Modèle {model_name} non disponible.'
                    continue
                else:
                    # Autre erreur, essayer le modèle suivant
                    error_text = api_response.text[:200]
                    print(f"✗ Modèle {model_name}: erreur {api_response.status_code}, essai du modèle suivant...")
                    last_error = f'Erreur API Gemini (code {api_response.status_code}): {error_text}'
                    continue
                    
            except requests.exceptions.Timeout:
                last_error = 'Timeout lors de la connexion à l\'API Gemini. Veuillez réessayer.'
                continue
            except requests.exceptions.RequestException as e:
                last_error = f'Erreur de connexion à l\'API Gemini: {str(e)[:200]}'
                continue
        
        # Si aucun modèle n'a fonctionné, retourner la dernière erreur
        if last_error:
            if 'quota' in last_error.lower() or 'Limite' in last_error:
                return JsonResponse({
                    'error': 'Limite de requêtes atteinte pour tous les modèles. Veuillez réessayer plus tard ou vérifier votre quota API.',
                    'status': 'error'
                }, status=429)
            else:
                return JsonResponse({
                    'error': f'Aucun modèle Gemini disponible. {last_error}',
                    'status': 'error'
                }, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Format de données invalide',
            'status': 'error'
        }, status=400)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Erreur chatbot: {error_details}")  # Pour le débogage
        return JsonResponse({
            'error': f'Erreur inattendue: {str(e)}',
            'status': 'error'
        }, status=500)

