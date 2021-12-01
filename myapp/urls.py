from django.urls import path
from . import views 

urlpatterns=[
	path('',views.index,name='index'),
	path('about/',views.about,name='about'),
	path('contact/',views.contact,name='contact'),
	path('watches/',views.watches,name='watches'),
	path('signup/',views.signup,name='signup'),
	path('login/',views.login,name='login'),
	path('logout/',views.logout,name='logout'),
	path('seller_index/',views.seller_index,name='seller_index'),
	path('add_watches/',views.add_watches,name='add_watches'),
	path('view_watches/',views.view_watches,name='view_watches'),
	path('watch_detail/<int:pk>/',views.watch_detail,name='watch_detail'),
	path('user_watch_detail/<int:pk>/',views.user_watch_detail,name='user_watch_detail'),
	path('watch_edit/<int:pk>/',views.watch_edit,name='watch_edit'),
	path('watch_delete/<int:pk>/',views.watch_delete,name='watch_delete'),
	path('add_to_wishlist/<int:pk>/',views.add_to_wishlist,name='add_to_wishlist'),
	path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
	path('remove_from_wishlist/<int:pk>/',views.remove_from_wishlist,name='remove_from_wishlist'),
	path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
	path('mywishlist/',views.mywishlist,name='mywishlist'),
	path('mycart/',views.mycart,name='mycart'),
	path('change_qty/',views.change_qty,name='change_qty'),
	path('validate_email/',views.validate_email,name='validate_email'),
	path('validate_oldpassword/',views.validate_oldpassword,name='validate_oldpassword'),
	path('forgot_password/',views.forgot_password,name='forgot_password'),
	path('otp/',views.otp,name='otp'),
	path('new_password/',views.new_password,name='new_password'),
	path('change_password/',views.change_password,name='change_password'),
	path('profile/',views.profile,name='profile'),
	path('pay/', views.initiate_payment, name='pay'),
    path('callback/', views.callback, name='callback'),
    path('myorder/', views.myorder, name='myorder'),

	
]