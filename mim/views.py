from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import requests
from .form import MIMForm, CommentForm
from .models import MIM, LastSubmission, Vote, Comment
from PIL import Image
import cv2
import os
from django.db.models import Count, Q
from datetime import timedelta

def format_memes(memes_list, request):
    ip_address = request.META.get('REMOTE_ADDR')
    memes_with_votes = []
    for meme in memes_list:
        file_path = meme.file.path
        is_video = meme.file.name.lower().endswith('.mp4')
        width, height = get_meme_dimensions(file_path) if os.path.exists(file_path) else (0, 0)

        format_class = 'square'
        area = width * height
        if width > 0 and height > 0:
            aspect_ratio = width / height
            if aspect_ratio > 4:
                format_class = 'wide-low'
            elif is_video:
                if aspect_ratio > 1.5:
                    format_class = 'horizontal-video'
                elif aspect_ratio < 0.7:
                    format_class = 'vertical-video'
                else:
                    format_class = 'square-video'
            else:
                if aspect_ratio > 1.2:
                    format_class = 'horizontal-image'
                elif aspect_ratio < 0.8:
                    format_class = 'vertical-image'
                else:
                    format_class = 'square'

        comment_count = Comment.objects.filter(meme=meme).count()
        memes_with_votes.append({
            'meme': meme,
            'has_voted': Vote.objects.filter(meme=meme, ip_address=ip_address).exists() and Vote.objects.get(meme=meme, ip_address=ip_address).is_like,
            'format_class': format_class,
            'area': area,
            'comment_count': comment_count
        })
    return memes_with_votes

def discord_logout(request):
    if request.user.is_authenticated:
        # Отримуємо токен доступу з social-auth
        try:
            social = request.user.social_auth.get(provider='discord')
            access_token = social.extra_data.get('access_token')
            if access_token:
                # Анулюємо токен через Discord API
                revoke_url = 'https://discord.com/api/oauth2/token/revoke'
                data = {
                    'client_id': 'твій_client_id',  # Заміни на свій Client ID
                    'client_secret': 'твій_client_secret',  # Заміни на свій Client Secret
                    'token': access_token,
                }
                response = requests.post(revoke_url, data=data)
                response.raise_for_status()  # Перевірка на помилки
        except Exception as e:
            # Якщо щось пішло не так, просто ігноруємо (логін все одно завершиться)
            print(f"Ошибка при анулюванні токена: {e}")

        # Завершуємо локальну сесію
        logout(request)

    # Перенаправляємо на головну сторінку
    return redirect('/')

def get_meme_dimensions(file_path):
    try:
        if file_path.lower().endswith('.mp4'):
            cap = cv2.VideoCapture(file_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
        else:
            with Image.open(file_path) as img:
                width, height = img.size
        return width, height
    except Exception as e:
        print(f"Error getting dimensions for {file_path}: {e}")
        return 0, 0

@csrf_protect
def memes(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            meme_id = request.POST.get('meme_id')
            action = request.POST.get('action')
            ip_address = request.META.get('REMOTE_ADDR')

            if not meme_id or not action:
                return HttpResponseBadRequest('Missing meme_id or action')

            if action == 'like':
                try:
                    meme = MIM.objects.get(meme_id=meme_id)
                    vote = Vote.objects.filter(meme=meme, ip_address=ip_address).first()

                    if vote and vote.is_like:
                        meme.likes -= 1
                        vote.delete()
                    else:
                        if vote:
                            vote.delete()
                        meme.likes += 1
                        Vote.objects.create(meme=meme, ip_address=ip_address, is_like=True)
                    meme.save()

                    return JsonResponse({'success': True, 'likes': meme.likes})
                except MIM.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Meme does not exist'}, status=404)
            return HttpResponseBadRequest('Invalid action')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    elif request.method == 'POST':
        return JsonResponse({'success': False, 'error': 'Please log in with Discord to like memes'}, status=403)

    memes_list = MIM.objects.order_by('-uploaded_at')
    memes_with_votes = format_memes(memes_list, request)
    return render(request, 'mim/memes.html', {'memes_with_votes': memes_with_votes})

@csrf_protect
def top_memes(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            meme_id = request.POST.get('meme_id')
            action = request.POST.get('action')
            ip_address = request.META.get('REMOTE_ADDR')

            if not meme_id or not action:
                return HttpResponseBadRequest('Missing meme_id or action')

            if action == 'like':
                try:
                    meme = MIM.objects.get(meme_id=meme_id)
                    vote = Vote.objects.filter(meme=meme, ip_address=ip_address).first()

                    if vote and vote.is_like:
                        meme.likes -= 1
                        vote.delete()
                    else:
                        if vote:
                            vote.delete()
                        meme.likes += 1
                        Vote.objects.create(meme=meme, ip_address=ip_address, is_like=True)
                    meme.save()

                    return JsonResponse({'success': True, 'likes': meme.likes})
                except MIM.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Meme does not exist'}, status=404)
            return HttpResponseBadRequest('Invalid action')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    elif request.method == 'POST':
        return JsonResponse({'success': False, 'error': 'Please log in with Discord to like memes'}, status=403)

    memes_list = MIM.objects.order_by('-likes')
    memes_with_votes = format_memes(memes_list, request)
    return render(request, 'mim/top_memes.html', {'memes_with_votes': memes_with_votes})

@csrf_protect
def trending_memes(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            meme_id = request.POST.get('meme_id')
            action = request.POST.get('action')
            ip_address = request.META.get('REMOTE_ADDR')

            if not meme_id or not action:
                return HttpResponseBadRequest('Missing meme_id or action')

            if action == 'like':
                try:
                    meme = MIM.objects.get(meme_id=meme_id)
                    vote = Vote.objects.filter(meme=meme, ip_address=ip_address).first()

                    if vote and vote.is_like:
                        meme.likes -= 1
                        vote.delete()
                    else:
                        if vote:
                            vote.delete()
                        meme.likes += 1
                        Vote.objects.create(meme=meme, ip_address=ip_address, is_like=True)
                    meme.save()

                    return JsonResponse({'success': True, 'likes': meme.likes})
                except MIM.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Meme does not exist'}, status=404)
            return HttpResponseBadRequest('Invalid action')
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    elif request.method == 'POST':
        return JsonResponse({'success': False, 'error': 'Please log in with Discord to like memes'}, status=403)

    time_threshold = timezone.now() - timedelta(hours=24)
    time_filter = request.GET.get('time', '24h')
    if time_filter == '7d':
        time_threshold = timezone.now() - timedelta(days=7)
    elif time_filter == '1h':
        time_threshold = timezone.now() - timedelta(hours=1)

    memes_list = MIM.objects.annotate(
        recent_likes=Count('votes', filter=Q(votes__is_like=True, votes__meme__uploaded_at__gte=time_threshold)),
        recent_comments=Count('comments', filter=Q(comments__created_at__gte=time_threshold))
    ).order_by('-recent_likes', '-recent_comments', '-uploaded_at')

    memes_with_votes = format_memes(memes_list, request)
    return render(request, 'mim/trending.html', {'memes_with_votes': memes_with_votes, 'time_filter': time_filter})

@login_required(login_url='/login/')
def upload_meme(request):
    if request.method == 'POST':
        form = MIMForm(request.POST, request.FILES)
        if form.is_valid():
            meme = form.save(commit=False)
            meme.user = request.user
            discord_data = request.user.social_auth.get(provider='discord').extra_data
            user_id = discord_data.get('id')
            avatar_hash = discord_data.get('avatar')
            if user_id and avatar_hash:
                meme.avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=128"
            meme.save()
            LastSubmission.objects.all().delete()
            LastSubmission.objects.create()
            return redirect('memes')
    else:
        form = MIMForm()

    last_submit = LastSubmission.objects.first()
    cooldown = 1 * 5
    if last_submit:
        time_left = cooldown - (timezone.now() - last_submit.timestamp).total_seconds()
        time_left = max(0, int(time_left))
    else:
        time_left = 0

    return render(request, 'mim/upload.html', {'form': form, 'time_left': time_left})

@login_required(login_url='/login/')
def meme_detail(request, meme_id):
    meme = MIM.objects.get(meme_id=meme_id)
    file_path = meme.file.path
    is_video = meme.file.name.lower().endswith('.mp4')
    width, height = get_meme_dimensions(file_path) if os.path.exists(file_path) else (0, 0)

    format_class = 'square'
    if width > 0 and height > 0:
        aspect_ratio = width / height
        if aspect_ratio > 4:
            format_class = 'wide-low'
        elif is_video:
            if aspect_ratio > 1.5:
                format_class = 'horizontal-video'
            elif aspect_ratio < 0.7:
                format_class = 'vertical-video'
            else:
                format_class = 'square-video'
        else:
            if aspect_ratio > 1.2:
                format_class = 'horizontal-image'
            elif aspect_ratio < 0.8:
                format_class = 'vertical-image'
            else:
                format_class = 'square'

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.meme = meme
            comment.user = request.user
            comment.avatar = request.user.social_auth.get(provider='discord').extra_data.get('avatar_url', '')
            comment.save()
            return redirect('meme_detail', meme_id=meme_id)
    else:
        form = CommentForm()

    comments = Comment.objects.filter(meme=meme).order_by('-created_at')
    return render(request, 'mim/mim_info.html', {'meme': meme, 'format_class': format_class, 'form': form, 'comments': comments})