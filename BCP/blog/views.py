from django.shortcuts import render,get_object_or_404,redirect,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.mixins import LoginRequiredMixin # just like decorators
from django.utils import timezone
from django.views.generic import TemplateView,ListView,DetailView,CreateView,DeleteView,UpdateView
from django.urls import reverse_lazy
from .models import Post,Comment
from blog.forms import CommentForm,PostForm


class AboutView(TemplateView):
    template_name = 'blog/about.html'

#------------------------------------------Posts-------------------------------------------------------------------
class PostListView(ListView):
    model = Post
    # __lte -> less than or equal to
    # - means desending first
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post

class CreatePostView(LoginRequiredMixin,CreateView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostUpdateView(UpdateView,LoginRequiredMixin):
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(DeleteView,LoginRequiredMixin):
    model = Post
    success_url = reverse_lazy('post_list')

class DraftListView(LoginRequiredMixin,ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_draft_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('create_date')

#------------------------------------------Comments----------------------------------------------------------------

@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=pk)

@login_required
def add_comment_to_post(request,pk):
    # pk links the comment to the post
    post = get_object_or_404(Post,pk=pk)
    #get_list_or_404: get that object and if you couldn't find that page display 404
    if request.method == 'POST':
        #form filled and submitted
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False) #saves the form in the memory
            comment.post = post # object of the class
            comment.save() # saving it in DB
            return  redirect('post_detail',pk=post.pk)

    else:
        # if the form is not submitted
        form = CommentForm()
    return render(request,'blog/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    comment.approve() #calling method from the models.Comment
    return redirect('post_detail',pk=comment.post.pk)

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment,pk=pk)
    post_pk = comment.post.pk
    comment.delete() # this deletes all the details of the comments that's why we're saving the pk in a variable
    return redirect('post_detail',pk=post_pk)


