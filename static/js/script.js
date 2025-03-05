// Глобальна змінна для статичних URL
const staticUrl = (path) => `${window.location.origin}/static/${path}`;

window.addEventListener('load', function() {
    setTimeout(function() {
        document.body.classList.remove('loaded');
        document.getElementById('loader').style.display = 'none';
    }, 0);
});

document.addEventListener('DOMContentLoaded', function () {
    // Ледаче завантаження мемів
    const lazyMemes = document.querySelectorAll('.lazy-meme');
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const meme = entry.target;
                if (meme.tagName.toLowerCase() === 'img') {
                    meme.src = meme.getAttribute('data-src');
                    meme.onerror = () => console.warn('Image failed to load:', meme);
                } else if (meme.tagName.toLowerCase() === 'video') {
                    const source = meme.querySelector('source');
                    if (source) {
                        source.src = source.getAttribute('data-src');
                        source.onerror = () => console.warn('Video source failed to load:', source);
                        meme.load();
                    }
                }
                meme.classList.add('loaded');
                observer.unobserve(meme);
            }
        });
    }, {
        rootMargin: '50px',
        threshold: 0.1
    });

    lazyMemes.forEach(meme => observer.observe(meme));

    // Обробка опису
    const descriptions = document.querySelectorAll('.description');
    descriptions.forEach((desc) => {
        desc.addEventListener('click', function () {
            this.classList.toggle('active');
            const content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });

    // Обробка лайків
    document.querySelectorAll('.like-btn').forEach((btn) => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            console.log('Like button clicked, memeId:', this.closest('.social-form').getAttribute('data-meme-id')); // Дебаг
            const isAuthenticated = '{{ user.is_authenticated|default:"false" | lower }}' === 'true';
            console.log('Is authenticated:', isAuthenticated); // Дебаг
            if (!isAuthenticated) {
                alert('Please log in with Discord to like memes.');
                return;
            }
            const memeId = this.closest('.social-form').getAttribute('data-meme-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            const likeIcon = this.querySelector('.like-icon');
            const likesCount = this.querySelector('p');

            const csrfToken = getCSRFToken();
            console.log('CSRF Token:', csrfToken); // Дебаг
            if (!csrfToken) {
                alert('CSRF token not found. Please refresh the page.');
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
                        this.setAttribute('data-liked', data.has_voted.toString());
                    } else {
                        alert(data.error || 'Failed to like meme.');
                    }
                })
                .catch(error => {
                    console.error('Error liking meme:', error);
                    alert('An error occurred. Please try again or check the console.');
                });
        });
    });

    // Обробка share
    document.querySelectorAll('.share-btn').forEach((btn) => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const memeId = this.closest('.social-form').getAttribute('data-meme-id');
            const memeUrl = `${window.location.origin}/mim/meme_detail/${memeId}/`;
            navigator.clipboard.writeText(memeUrl)
                .then(() => {
                    alert('URL copied to clipboard!');
                })
                .catch((err) => {
                    console.error('Failed to copy URL:', err);
                    alert('Failed to copy URL.');
                });
        });
    });
});

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