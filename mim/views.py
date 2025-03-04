from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from .form import MIMForm, CommentForm
from .models import MIM, LastSubmission, Vote, Comment
from PIL import Image
import cv2
import os
from django.db.models import Count, Q
from django.conf import settings
from django.templatetags.static import static
from datetime import timedelta
from django.contrib.auth import logout
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import logging
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_meme_dimensions(file_path):
    try:
        if file_path.lower().endswith('.mp4'):
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                logger.error(f"Cannot open video file: {file_path}")
                return 0, 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
        else:
            with Image.open(file_path) as img:
                width, height = img.size
        return width, height
    except Exception as e:
        logger.error(f"Error getting dimensions for {file_path}: {e}")
        return 0, 0

def format_memes(memes_list, request):
    memes_with_votes = []
    for meme in memes_list:
        has_voted = False
        like_icon = static('img/like.png')
        if request.user.is_authenticated:
            has_voted = Vote.objects.filter(meme=meme, user=request.user, is_like=True).exists()
            like_icon = static('img/like2.png') if has_voted else static('img/like.png')
        file_path = meme.file.path
        is_video = meme.file.name.lower().endswith('.mp4')
        width, height = get_meme_dimensions(file_path) if os.path.exists(file_path) else (0, 0)
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")

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
        likes = meme.likes

        logger.debug(f"Meme {meme.meme_id}: likes={likes}, comment_count={comment_count}, file_path={file_path}")
        memes_with_votes.append({
            'meme': meme,
            'has_voted': has_voted,
            'like_icon': like_icon,
            'format_class': format_class,
            'area': area,
            'comment_count': comment_count
        })
    return memes_with_votes

@csrf_protect
@cache_page(60 * 15)    
def memes(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            meme_id = request.POST.get('meme_id')
            action = request.POST.get('action')

            if not meme_id or not action:
                return HttpResponseBadRequest('Missing meme_id or action')

            if action == 'like':
                try:
                    meme = MIM.objects.get(meme_id=meme_id)
                    vote = Vote.objects.filter(meme=meme, user=request.user).first()

                    if vote and vote.is_like:
                        meme.likes -= 1
                        vote.delete()
                    else:
                        if vote:
                            vote.delete()
                        meme.likes += 1
                        Vote.objects.create(meme=meme, user=request.user, is_like=True)
                    meme.save()
                    has_voted = Vote.objects.filter(meme=meme, user=request.user, is_like=True).exists()
                    return JsonResponse({'success': True, 'likes': meme.likes, 'has_voted': has_voted})
                except MIM.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Meme does not exist'}, status=404)
            return HttpResponseBadRequest('Invalid action')
        except Exception as e:
            logger.error(f"Error in POST request: {e}")
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

            if not meme_id or not action:
                return HttpResponseBadRequest('Missing meme_id or action')

            if action == 'like':
                try:
                    meme = MIM.objects.get(meme_id=meme_id)
                    vote = Vote.objects.filter(meme=meme, user=request.user).first()

                    if vote and vote.is_like:
                        meme.likes -= 1
                        vote.delete()
                    else:
                        if vote:
                            vote.delete()
                        meme.likes += 1
                        Vote.objects.create(meme=meme, user=request.user, is_like=True)
                    meme.save()
                    has_voted = Vote.objects.filter(meme=meme, user=request.user, is_like=True).exists()
                    return JsonResponse({'success': True, 'likes': meme.likes, 'has_voted': has_voted})
                except MIM.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Meme does not exist'}, status=404)
            return HttpResponseBadRequest('Invalid action')
        except Exception as e:
            logger.error(f"Error in POST request: {e}")
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

            if not meme_id or not action:
                return HttpResponseBadRequest('Missing meme_id or action')

            if action == 'like':
                try:
                    meme = MIM.objects.get(meme_id=meme_id)
                    vote = Vote.objects.filter(meme=meme, user=request.user).first()

                    if vote and vote.is_like:
                        meme.likes -= 1
                        vote.delete()
                    else:
                        if vote:
                            vote.delete()
                        meme.likes += 1
                        Vote.objects.create(meme=meme, user=request.user, is_like=True)
                    meme.save()
                    has_voted = Vote.objects.filter(meme=meme, user=request.user, is_like=True).exists()
                    return JsonResponse({'success': True, 'likes': meme.likes, 'has_voted': has_voted})
                except MIM.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Meme does not exist'}, status=404)
            return HttpResponseBadRequest('Invalid action')
        except Exception as e:
            logger.error(f"Error in POST request: {e}")
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

@login_required(login_url='/login/discord/')
def upload_meme(request):
    if request.method == 'POST':
        form = MIMForm(request.POST, request.FILES)
        if form.is_valid():
            meme = form.save(commit=False)
            meme.user = request.user
            try:
                social = request.user.social_auth.filter(provider='discord').first()
                if social:
                    discord_data = social.extra_data
                    user_id = discord_data.get('id')
                    avatar_hash = discord_data.get('avatar')
                    print(f"Discord data: {discord_data}")
                    if user_id and avatar_hash:
                        meme.avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=128"
                    else:
                        meme.avatar = ''
                else:
                    print("No Discord social authfound for user")
                    meme.avatar = ''
            except Exception as e:
                print(f"Error fetching avatar: {e}")
                meme.avatar = ''
            meme.description = request.POST.get('description', '')
            try:
                meme.save()
                print("Meme saved successfully")
                LastSubmission.objects.all().delete()
                LastSubmission.objects.create()
            except Exception as e:
                print(f"Error saving meme: {e}")
                return JsonResponse({'success': False, 'error': f'Failed to save meme: {str(e)}'})
            return JsonResponse({'success': True, 'message': 'File uploaded successfully'})
        else:
            print(f"Form errors: {form.errors}")
            return JsonResponse({'success': False, 'error': form.errors})
    else:
        form = MIMForm()

    last_submit = LastSubmission.objects.first()
    cooldown = 1 * 5
    if last_submit:
        time_left = cooldown - (timezone.now() - last_submit.timestamp).total_seconds()
        time_left = max(0, int(time_left))
    else:
        time_left = 0

    user_meme_list = MIM.objects.filter(user=request.user).order_by('-uploaded_at') if request.user.is_authenticated else []
    user_meme_count = user_meme_list.count() if user_meme_list else 0
    has_discord_account = request.user.social_auth.filter(provider='discord').exists()

    return render(request, 'mim/upload.html', {
        'form': form,
        'time_left': time_left,
        'user_meme_list': user_meme_list,
        'user_meme_count': user_meme_count,
        'has_discord_account': has_discord_account
    })

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
        if not request.user.is_authenticated:
            return redirect('/login/discord/?next=' + request.path)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.meme = meme
            comment.user = request.user
            try:
                social = request.user.social_auth.filter(provider='discord').first()
                if social:
                    discord_data = social.extra_data
                    user_id = discord_data.get('id')
                    avatar_hash = discord_data.get('avatar')
                    print(f"Discord data: {discord_data}")
                    if user_id and avatar_hash:
                        comment.avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png?size=128"
                    else:
                        comment.avatar = ''
                else:
                    print("No Discord social auth found for user")
                    comment.avatar = ''
            except Exception as e:
                print(f"Error fetching avatar: {e}")
                comment.avatar = ''
            comment.save()
            return redirect('mim:meme_detail', meme_id=meme_id)
    else:
        form = CommentForm()

    comments = Comment.objects.filter(meme=meme).order_by('-created_at')
    return render(request, 'mim/mim_info.html', {'meme': meme, 'format_class': format_class, 'form': form, 'comments': comments})

def discord_logout(request):
    if request.user.is_authenticated:
        try:
            social = request.user.social_auth.filter(provider='discord').first()
            if social:
                access_token = social.extra_data.get('access_token')
                if access_token:
                    revoke_url = 'https://discord.com/api/oauth2/token/revoke'
                    data = {
                        'client_id': '1342972978266243158',
                        'client_secret': 'DmU8TacN5R5PVwyEFmheqODSJG1IaBHr',
                        'token': access_token,
                    }
                    response = requests.post(revoke_url, data=data)
                    response.raise_for_status()
        except Exception as e:
            print(f"an error occured {e}")
        logout(request)
    return redirect('/')