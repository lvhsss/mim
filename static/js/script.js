
window.addEventListener('load', function() {
    setTimeout(function() {
        document.body.classList.remove('loaded');
        document.getElementById('loader').style.display = 'none';
    }, 0);
});
// "use strict"

// const nav__links = document.querySelector('.tabs-brg');
// const body = document.querySelector('body')

// if (nav__links) {
//     const menu = document.querySelector('.burger-menu');
//     menu.addEventListener("click", function(e) {
//         body.classList.toggle('_lock')
//         menu.classList.toggle('_active');
//         nav__links.classList.toggle('_active');
//     })
// }


document.addEventListener("DOMContentLoaded", function () {
document.querySelectorAll('.description').forEach(description => {
    const memeId = description.id.split('-')[1];
    const showMoreBtn = document.getElementById(`show-more-${memeId}`);

    if (description.scrollHeight > description.clientHeight) {
        showMoreBtn.style.display = 'block';
    }

    showMoreBtn.addEventListener('click', function () {
        if (description.classList.contains('expanded')) {
            description.classList.remove('expanded');
            showMoreBtn.textContent = 'show more ..';
        } else {
            description.classList.add('expanded');
            showMoreBtn.textContent = 'show less ..';
        }
    });
});

const currentPage = window.location.pathname;
if (currentPage.includes("memes")) {
    const lastMemeId = sessionStorage.getItem('lastViewedMemeIdNew');
    if (lastMemeId) {
        const scrollPosition = parseInt(sessionStorage.getItem(`scrollPositionNew_${lastMemeId}`), 10);
        if (!isNaN(scrollPosition)) {
            setTimeout(() => {
                const headerHeight = document.querySelector('.header')?.offsetHeight || 70;
                window.scrollTo({
                    top: Math.max(scrollPosition + headerHeight - 20, 0),
                    behavior: "smooth"
                });
            }, 100);
        }
    }
}

const lazyMemes = document.querySelectorAll('.lazy-meme');
    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const meme = entry.target;
                if (meme.tagName.toLowerCase() === 'img') {
                    meme.src = meme.getAttribute('data-src');
                } else if (meme.tagName.toLowerCase() === 'video') {
                    const source = meme.querySelector('source');
                    if (source) source.src = source.getAttribute('data-src');
                    meme.load(); // Перезапускаємо відео
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
});

document.querySelectorAll('.meme-block a').forEach(link => {
    link.addEventListener('click', function () {
        const memeBlock = this.closest('.meme-block');
        const memeId = memeBlock.getAttribute('data-meme-id');
        const scrollPosition = window.scrollY || window.pageYOffset;
        sessionStorage.setItem(`scrollPositionNew_${memeId}`, scrollPosition);
        sessionStorage.setItem('lastViewedMemeIdNew', memeId);
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
    return cookieValue;
}

document.querySelectorAll('.like-btn').forEach(btn => {
    const memeId = btn.closest('.social-form').getAttribute('data-meme-id');
    const isLiked = btn.getAttribute('data-liked') === 'true';
    const likeIcon = btn.querySelector('.like-icon');
    const likesCount = btn.querySelector('p');
});

document.querySelectorAll('.like-btn').forEach(btn => {
btn.addEventListener('click', function (e) {
    e.preventDefault();
    const isAuthenticated = '{{ user.is_authenticated|default:"false" | lower }}' === "true";
    if (!isAuthenticated) {
        alert('Please log in with Discord to like memes.');
        return;
    }
    const memeId = this.closest('.social-form').getAttribute('data-meme-id');
    const isLiked = this.getAttribute('data-liked') === 'true';
    const likeIcon = this.querySelector('.like-icon');
    const likesCount = this.querySelector('p');

    const formData = new FormData();
    formData.append('meme_id', memeId);
    formData.append('action', 'like');

    fetch(window.location.pathname, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                likesCount.textContent = data.likes;
                likeIcon.src = data.has_voted ? "{% static 'img/like2.png' %}" : "{% static 'img/like.png' %}";
                this.setAttribute('data-liked', data.has_voted.toString());
            } else {
                alert(data.error || 'Failed to like meme.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Please log in with Discord to like memes.');
        });
    });
});

document.querySelectorAll('.share-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.preventDefault();
        const memeId = this.getAttribute('data-meme-id');
        const memeUrl = `${window.location.origin}/memes/${memeId}/`;
        navigator.clipboard.writeText(memeUrl).then(() => {
            const message = document.createElement('div');
            message.className = 'copy-message';
            message.textContent = 'Link copied to clipboard!';
            document.body.appendChild(message);
            message.style.position = 'fixed';
            message.style.top = '50%';
            message.style.left = '50%';
            message.style.transform = 'translate(-50%, -50%)';
            message.style.backgroundColor = '#4CAF50';
            message.style.color = 'white';
            message.style.padding = '10px 20px';
            message.style.borderRadius = '5px';
            message.style.zIndex = '1000';
            setTimeout(() => message.remove(), 1000);
        }).catch(err => {
            alert('Failed to copy link.');
        });
    });
});
