window.addEventListener('load', function() {
    setTimeout(function() {
        document.body.classList.remove('loaded');
        document.getElementById('loader').style.display = 'none';
    }, 0);
});

// Глобальна змінна для статичних URL
const staticUrl = (path) => `${window.location.origin}/static/${path}`;

document.addEventListener('DOMContentLoaded', function () {
    // Ледаче завантаження мемів
    const lazyMemes = document.querySelectorAll('.lazy-meme');
    if (lazyMemes.length > 0) {
        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting && entry.target) {
                    const meme = entry.target;
                    if (meme.tagName && meme.tagName.toLowerCase() === 'img' && meme.style) {
                        meme.src = meme.getAttribute('data-src');
                        meme.onerror = () => console.warn('Image failed to load:', meme);
                    } else if (meme.tagName && meme.tagName.toLowerCase() === 'video' && meme.style) {
                        const source = meme.querySelector('source');
                        if (source) {
                            source.src = source.getAttribute('data-src');
                            source.onerror = () => console.warn('Video source failed to load:', source);
                            meme.load();
                        }
                    }
                    if (meme.classList) meme.classList.add('loaded');
                    observer.unobserve(meme);
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.1
        });

        lazyMemes.forEach(meme => observer.observe(meme));
    } else {
        console.log('No lazy-meme elements found');
    }

    // Обробка опису
    const descriptions = document.querySelectorAll('.description');
    descriptions.forEach((desc) => {
        if (desc && desc.style) {
            desc.addEventListener('click', function () {
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                if (content && content.style) {
                    if (content.style.maxHeight) {
                        content.style.maxHeight = null;
                    } else {
                        content.style.maxHeight = content.scrollHeight + 'px';
                    }
                }
            });
        }
    });

    // Обробка лайків
    document.querySelectorAll('.like-btn').forEach((btn) => {
        if (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                console.log('Like button clicked, memeId:', this.closest('.social-form')?.getAttribute('data-meme-id')); // Дебаг
                checkAuthentication(this);
            });
        }
    });

    // Обробка share
    document.querySelectorAll('.share-btn').forEach((btn) => {
        if (btn) {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                const memeId = this.closest('.social-form')?.getAttribute('data-meme-id');
                if (memeId) {
                    const memeUrl = `${window.location.origin}/mim/meme_detail/${memeId}/`;
                    navigator.clipboard.writeText(memeUrl)
                        .then(() => {
                            showCustomAlert('URL copied to clipboard!');
                        })
                        .catch((err) => {
                            console.error('Failed to copy URL:', err);
                            showCustomAlert('Failed to copy URL.');
                        });
                }
            });
        }
    });

    // Стилізоване повідомлення
    function showCustomAlert(message) {
        const alertBox = document.createElement('div');
        alertBox.className = 'custom-alert';
        alertBox.textContent = message;
        document.body.appendChild(alertBox);

        setTimeout(() => {
            alertBox.style.opacity = '1';
        }, 10);

        setTimeout(() => {
            alertBox.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(alertBox);
            }, 300);
        }, 3000);

        alertBox.addEventListener('click', () => {
            alertBox.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(alertBox);
            }, 300);
        });
    }
});

function checkAuthentication(btn) {
    fetch('/check-auth/', {
        method: 'GET',
        credentials: 'same-origin'
    })
        .then(response => response.json())
        .then(data => {
            console.log('Authentication check:', data); // Дебаг
            if (data.is_authenticated) {
                handleLike(btn);
            } else {
                showCustomAlert('Please log in with Discord to like memes.');
            }
        })
        .catch(error => {
            console.error('Error checking authentication:', error);
            showCustomAlert('An error occurred. Please try again.');
        });
}

function handleLike(btn) {
    const memeId = btn.closest('.social-form')?.getAttribute('data-meme-id');
    if (!memeId) {
        console.error('Meme ID not found');
        showCustomAlert('Error finding meme. Please try again.');
        return;
    }
    const isLiked = btn.getAttribute('data-liked') === 'true';
    const likeIcon = btn.querySelector('.like-icon');
    const likesCount = btn.querySelector('p');

    const csrfToken = getCSRFToken();
    console.log('CSRF Token:', csrfToken); // Дебаг
    if (!csrfToken) {
        showCustomAlert('CSRF token not found. Please refresh the page.');
        return;
    }

    const formData = new FormData();
    formData.append('meme_id', memeId);
    formData.append('action', 'like');

    fetch(window.location.pathname, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        },
        credentials: 'same-origin'
    })
        .then(response => {
            console.log('Fetch response status:', response.status); // Дебаг
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Fetch response data:', data); // Дебаг
            if (data.success) {
                likesCount.textContent = data.likes;
                likeIcon.src = data.has_voted ? staticUrl('img/like2.png') : staticUrl('img/like.png');
                btn.setAttribute('data-liked', data.has_voted.toString());
            } else {
                showCustomAlert(data.error || 'Failed to like meme.');
            }
        })
        .catch(error => {
            console.error('Error liking meme:', error);
            showCustomAlert('An error occurred. Please try again or check the console.');
        });
}

function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue || '';
}

"use strict";

const nav__links = document.querySelector('.tabs-brg');
const body = document.querySelector('body')

if (nav__links) {
    const menu = document.querySelector('.burger-menu');
    menu.addEventListener("click", function(e) {
        body.classList.toggle('_lock')
        menu.classList.toggle('_active');
        nav__links.classList.toggle('_active');
    })
}