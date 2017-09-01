from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from urllib.parse import quote
from django.utils import timezone
from django.db.models import Q

# Create your views here.
from .forms import PostForm
from .models import Post

# def post_home(request):
# 	return HttpResponse("<h1>Hello</h1>")

def post_create(request):
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	form = PostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		instance = form.save(commit=False)
		#print(form.cleaned_data.get("title"))
		instance.user = request.user
		instance.save()
	# else:
	# 	messages.error(request, "Not Successfully Created")

	# if request.method == "POST":
	# 	print "title" + request.POST.get("content")
	# 	print request.POST.get("title")
	# 	#Post.objects.create(title=title)
		# message success
		messages.success(request, "Successfully Created")
		return HttpResponseRedirect(instance.get_absolute_url())
	context = {
		"form": form,
	}
	return render(request, "post_form.html", context)
	#return HttpResponse("<h1>Create</h1>")

def post_detail(request, slug=None): #retrieve
	#instance = Post.objects.get(id=1)
	instance = get_object_or_404(Post, slug=slug)
	if instance.publish > timezone.now().date() or instance.draft:
		if not request.user.is_staff or not request.user.is_superuser:
			raise Http404
	share_string = quote(instance.content)
	context = {
	    "title": instance.title,
	    "instance": instance,
	    "share_string": share_string,
	}
	return render(request, "post_detail.html", context)
	#return HttpResponse("<h1>Detail</h1>")

def post_list(request): #list items
	# queryset = Post.objects.all()
	# context = {
	# 	"object_list": queryset, 
	# 	"title": "List",
	# 	"page_request_var": page_request_var
	# }
	
	# # if request.user.is_authenticated():
	# # 	context = {
	# # 		"title": "My User List"
	# # 	}
	# # else:
	# # 	context = {
	# # 		"title": "List"
	# # 	}
	# return render(request, "post_list.html", context)

	#return HttpResponse("<h1>List</h1>")

	#queryset_list = Post.objects.all() #.order_by("-timestamp")
	today = timezone.now().date()
	queryset_list = Post.objects.active() #.order_by("-timestamp")
	if request.user.is_staff or request.user.is_superuser:
		queryset_list = Post.objects.all()
	query = request.GET.get("q")
	if query:
		queryset_list = queryset_list.filter(
				Q(title__icontains=query)|
				Q(content__icontains=query)|
				Q(user__first_name__icontains=query) |
				Q(user__last_name__icontains=query)
				).distinct()
	paginator = Paginator(queryset_list, 2) # Show 25 contacts per page
	paginator = Paginator(queryset_list, 2) # Show 25 contacts per page
	page_request_var = "page"
	page = request.GET.get(page_request_var)
	try:
		queryset = paginator.page(page)
	except PageNotAnInteger:
		# If page is not an integer, deliver first page.
		queryset = paginator.page(1)
	except EmptyPage:
		# If page is out of range (e.g. 9999), deliver last page of results.
		queryset = paginator.page(paginator.num_pages)


	context = {
		"object_list": queryset, 
		"title": "List",
		"page_request_var": page_request_var,
		"today": today,
	}
	return render(request, "post_list.html", context)


def post_update(request, slug=None):
	#return HttpResponse("<h1>Update</h1>")
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	form = PostForm(request.POST or None, request.FILES or None, instance=instance)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "<a href='#'>Item</a> Saved", extra_tags='html_safe')
		return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"title": instance.title,
		"instance": instance,
		"form":form,
	}
	return render(request, "post_form.html", context)

def post_delete(request, slug=None):
	#return HttpResponse("<h1>Delete</h1>")
	if not request.user.is_staff or not request.user.is_superuser:
		raise Http404
	instance = get_object_or_404(Post, slug=slug)
	instance.delete()
	messages.success(request, "Successfully deleted")
	return redirect("posts:list")