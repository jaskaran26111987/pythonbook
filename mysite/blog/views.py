from django.shortcuts import render, get_object_or_404
from blog.models import Post, Comment
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from blog.forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
# page_number = 101

def post_detail(request, year, month, day, post):
  post = get_object_or_404(
                            Post, 
                            status  = Post.Status.PUBLISHED,
                            publish__year = year,
                            publish__month = month,
                            publish__day = day
                           )
  
  ''' 
  We have added a QuerySet to retrieve all active comments for the post, as follow
  This QuerySet is built using the post object. Instead of building a QuerySet for the Comment
  model directly, we leverage the post object to retrieve the related Comment objects. We use the
  comments manager for the related Comment objects that we previously defined in the Comment
  model, using the related_name attribute of the ForeignKey field to the Post model.
  
  # class Comment(models.Model):
  # post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
  
  related_name='comments'
  now post_obj.related_name.filter()
  post.comments.filter(active=True)
  '''
  comments = post.comments.filter(active=True)
  form = CommentForm()
  return render(request, 'blog/detail.html', {
                  'post':post,
                  'comments':comments,
                  'form':form
                })
@require_POST
def post_comment(request, post_id):
  post = get_object_or_404(
                            Post, 
                            id=post_id, 
                            status=Post.Status.PUBLISHED
                          )
  comment = None
  form = CommentForm(data = request.POST)
  if form.is_valid():
    comment = form.save(commit=False)
    comment.post = post
    comment.save()
  return render(
                request, 'blog/comment.html', 
                {'post':post, 'form':form, 'comment':comment}
              )


def post_share(request, post_id):
  post = get_object_or_404(Post, id = post_id, status=Post.Status.PUBLISHED)
  sent = False
  if request.method =='POST':
    form= EmailPostForm(request.POST)
    if form.is_valid():
      cd = form.cleaned_data
      post_url = request.build_absolute_uri( post.get_absolute_url())
      subject = f"{cd['name']} recommends you read" \
                f"{post.title}"
      message = f"Read {post.title} at {post_url}\n\n" \
                f"{cd['name']}\'s comments: {cd['comments']}"
      send_mail(subject, message, 'jaskaranrajal@gmail.com', [cd['to']])
      sent = True
  else:
    form = EmailPostForm()
  return render(
                request, 'blog/share.html', 
                {'post':post, 'form': form, 'sent':sent}
              )

class PostListView(ListView):
  queryset = Post.published.all()
  context_object_name = 'posts'
  paginate_by = 1
  template_name = 'blog/list.html'

def post_list(request, tag_slug=None):
  post_list = Post.published.all()
  tag = None
  if tag_slug:
    tag=get_object_or_404(Tag, slug =tag_slug)
    post_list= post_list.filter(tags__in=[tag])
  paginator = Paginator(post_list,1)
  page_number = request.GET.get('page',1)
  try:
    posts = paginator.page(page_number)
  except EmptyPage:
    posts = paginator.page(paginator.num_pages)
  except PageNotAnInteger:
    posts = paginator.page(1)

  return render(request, 'blog/list.html', {'posts':posts, 'tag':tag})

# def post_detail(request, id):
  # try:
  #   post = Post.published.get(id=id)
  # except Post.DoesNotExist:
  #   raise Http404('No post found')  
  # post = get_object_or_404(
  #                           Post, 
  #                           id=id, 
  #                           status=Post.Status.PUBLISHED
  #                         )

# def post_detail(request, year, month, day, post):
#   post = get_object_or_404(
#     Post,
#     status= Post.Status.PUBLISHED,
#     slug = post,
#     publish__year = year,
#     publish__month = month,
#     publish__day = day
#   )
#   return render(request, 'blog/detail.html', {'post':post})