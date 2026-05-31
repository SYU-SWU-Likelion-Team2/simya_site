from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from posts.models import Post, Draft, FirewoodType, Comment, Reaction


@login_required
def index(request):
    mine = request.GET.get('mine')

    posts = Post.objects.filter(
        is_published=True,
        expires_at__gt=timezone.now()
    ).select_related('author')

    if mine:
        posts = posts.filter(author=request.user)

    for post in posts:
        post.is_mine = post.author == request.user
        post.fire_count = post.reactions.filter(reaction_type='fire').count()
        post.stay_count = post.reactions.filter(reaction_type='stay').count()
        post.comment_count = post.comments.count()

    return render(request, 'tonight/index.html', {'posts': posts, 'mine': mine})

@login_required
def write(request):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            request.session['draft_content'] = content
            return redirect('tonight:firewood')
    return render(request, 'tonight/write.html')

@login_required
def firewood(request):
    if request.method == 'POST':
        content = request.session.get('draft_content', '')
        duration = request.POST.get('duration', 'dawn')

        duration_map = {
            'short': FirewoodType.KINDLING,
            'dawn':  FirewoodType.FIREWOOD,
            'day':   FirewoodType.LOG,
        }

        post = Post.objects.create(
            author=request.user,
            content=content,
            firewood_type=duration_map.get(duration, FirewoodType.FIREWOOD),
        )
        post.publish()
        return redirect('tonight:index')

    return render(request, 'tonight/firewood.html')

@login_required
def detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_published=True)
    post.is_mine = post.author == request.user
    post.fire_count = post.reactions.filter(reaction_type='fire').count()
    post.stay_count = post.reactions.filter(reaction_type='stay').count()
    post.user_reacted_fire = post.reactions.filter(author=request.user, reaction_type='fire').exists()
    post.user_reacted_stay = post.reactions.filter(author=request.user, reaction_type='stay').exists()
    comments = post.comments.select_related('author').all()

    return render(request, 'tonight/detail.html', {
        'post': post,
        'comments': comments,
    })

@login_required
def edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method == 'POST':
        post.content = request.POST.get('content', post.content)
        post.save()
        return redirect('tonight:detail', post_id=post_id)  # ← post_id 확인
    return render(request, 'tonight/edit.html', {'post': post})

@login_required
def comments(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_published=True)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content and post.author != request.user:
            Comment.objects.create(post=post, author=request.user, content=content)
        return redirect('tonight:detail', post_id=post_id)
    all_comments = post.comments.select_related('author').all()
    return render(request, 'tonight/comments.html', {'post': post, 'comments': all_comments})

@login_required
def reaction(request, post_id):
    post = get_object_or_404(Post, pk=post_id, is_published=True)
    if request.method == 'POST':
        reaction_type = request.POST.get('reaction_type')
        if reaction_type in ['fire', 'stay']:
            existing = Reaction.objects.filter(post=post, author=request.user, reaction_type=reaction_type)
            if existing.exists():
                existing.delete()
            else:
                Reaction.objects.create(post=post, author=request.user, reaction_type=reaction_type)
        return redirect('tonight:detail', post_id=post_id)

    post.fire_count = post.reactions.filter(reaction_type='fire').count()
    post.stay_count = post.reactions.filter(reaction_type='stay').count()
    post.user_reacted_fire = post.reactions.filter(author=request.user, reaction_type='fire').exists()
    post.user_reacted_stay = post.reactions.filter(author=request.user, reaction_type='stay').exists()
    return render(request, 'tonight/reaction.html', {'post': post})

@login_required
def delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    if request.method == 'POST':
        post.delete()
    return redirect('tonight:index')