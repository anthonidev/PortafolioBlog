from django.utils import timezone
from django.shortcuts import render,redirect
from django.urls.base import reverse_lazy
from django.views.generic.base import View
from .models import BodyPost, SocialPost, SocialComment,Categories
from .forms import BodyPostForm, SocialCommentForm
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.views.generic.edit import UpdateView,DeleteView
from django.http import HttpResponseRedirect,HttpResponse
from django.db.models import Q
from accounts.models import Profile
from django.db.models import Count

class PostDetailView(View):
    def get(self,request,pk, *args, **kwargs):
        post=SocialPost.objects.get(pk=pk)
        categories=Categories.objects.all()
        form=BodyPostForm()
        comments=SocialComment.objects.filter(post=post).order_by('-create_on')
        bodyposts=BodyPost.objects.filter(post=post).order_by('create_on')
        formComment=SocialCommentForm()
        coutCate = SocialPost.objects.values('category').annotate(Count('category')).order_by('category')
        mylist = zip(categories, coutCate)
        context={
            'post':post,
            'form':form,
            'comments':comments,
            'bodyposts':bodyposts,
            'formComment':formComment,
            'mylist':mylist,
            
        }
        return render(request,'pages/social/detail.html',context)
    def post(self,request,pk, *args, **kwargs):
        post=SocialPost.objects.get(pk=pk)
        form=BodyPostForm(request.POST,request.FILES)
        
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
        context={
            'post':post,
            'form':form,
        }
        return redirect('social:post-detail', pk=pk)
# class CountCategory(View):
#     def get(self, request, *args, **kwargs):
#         query=self.request.GET.get('query')
#         cate=SocialPost.objects.filter(Q(category__name__icontains=query))
#         count=len(cate)
#         context ={
#             'count':count
#         }
#         return render(request,'pages/social/detail.html',context)




class PostEditView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=SocialPost
    fields=['body']
    template_name='pages/social/edit.html'
    
    
    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('social:post-detail',kwargs={'pk':pk})

    def test_func(self):
        post=self.get_object()
        return self.request.user==post.author

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=SocialPost
    template_name='pages/social/delete.html'
    success_url = reverse_lazy('home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post=SocialPost.objects.get(pk=post_pk)
        parent_comment = SocialComment.objects.get(pk=pk)
        formComment=SocialCommentForm(request.POST)
        if formComment.is_valid():
            new_comment = formComment.save(commit=False)
            new_comment.author =request.user  
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()
        return redirect('social:post-detail', pk=post_pk )

class CommentFather(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post=SocialPost.objects.get(pk= pk)
        formComment=SocialCommentForm(request.POST)
        if formComment.is_valid():
            new_comment = formComment.save(commit=False)
            new_comment.author =request.user  
            new_comment.post = post
            new_comment.save()
        return redirect('social:post-detail', pk=pk )
        
class AddBodyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post=SocialPost.objects.get(pk=pk)

        form=BodyPostForm(request.POST,request.FILES)
        

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()

        return redirect('social:post-detail', pk=pk)

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model=SocialComment
    template_name="pages/social/comment_delete.html"

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('social:post-detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentEditView(UpdateView):
    model = SocialComment
    fields = ['comment']
    template_name = 'pages/social/comment_edit.html'

    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('social:post-detail', kwargs={'pk':pk})
    #hacer que el editar sea seguro

class UserSearch(View):
    def get(self, request, *args, **kwargs):
        query=self.request.GET.get('query')
        profile_list=Profile.objects.filter(Q(user__username__icontains=query))
        context ={
            'profile_list':profile_list,
        }
        return render(request, 'pages/social/search.html',context)
    
