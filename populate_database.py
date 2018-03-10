# Import all necessary libraries

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, SubCategory, Items, Users

engine = create_engine('postgresql://postgres:happynewid@localhost/shoppingsite')   # noqa
'''
    Bind the engine to the metadata of the Base class so that the declaratives
    can be accessed through a DBSession instance
'''
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
'''
    A DBSession() instance establishes all conversations with the database
    and represents a "Staging-zone" for all the objects loaded into the
    database session object. Any change made against the objects in the
    session won't be persisted into the database until you call
    session.commit(). If you're not happy about the changes, you can revert
    all of them back to the last commit by caling session.rollback()
'''
session = DBSession()

# ***Create Dummy User***
User1 = Users(name='Shruti Sheoran', email="shruti.sheoran03@gmail.com",
              picture="",)
session.add(User1)
session.commit()

# ****Add Categories Men, Women, Kids, Electrical Appliances****

# Category Men

category1 = Category(name='Men',
                                         picture='http://www.99wtf.net/wp-content/uploads/2016/04/dark-brown-4.jpg',  # noqa
                                         user_id=1)
session.add(category1)
session.commit()

# Add Subcategories TopWear, BottomWear, Footwear, Fashion Accessories to Men
sub_category11 = SubCategory(user_id=1, name='TopWear', picture='http://static1.fashionbeans.com/wp-content/uploads/2017/09/aw17trendstop-8.jpg',  # noqa
                                                         category=category1)
session.add(sub_category11)
session.commit()

# Add items
item1 = Items(name='Bear printed T-shirt', picture='https://img0.etsystatic.com/145/0/15045808/il_340x270.1189662248_1qvv.jpg',  # noqa
                           price="$100", user_id=1, seller_name='Shruti',
                           seller_phoneno='8699609577', rating=5,
                           category=category1, sub_category=sub_category11)
session.add(item1)
session.commit()

item2 = Items(name=' Cotton Shirt', picture='https://li0.rightinthebox.com/images/384x500/201601/sfwbay1452137820394.jpg',  # noqa
                           price="$100", user_id=1, seller_name='Shruti',
                           seller_phoneno='8699609577', rating=5,
                           category=category1, sub_category=sub_category11)
session.add(item2)
session.commit()

sub_category12 = SubCategory(user_id=1, name='BottomWear', picture='https://assets.myntassets.com/h_1440,q_100,w_1080/v1/assets/images/1758782/2017/4/27/11493287149583-WROGN-Men-Grey-Slim-Fit-Solid-Joggers-1291493287149323-1.jpg',  # noqa
                                                         category=category1)
session.add(sub_category12)
session.commit()

sub_category13 = SubCategory(user_id=1, name='FootWear', picture='https://www.shoes.com/images/conceptshops/cs_mensshop_spring_styles_hero.jpg',  # noqa
                                                         category=category1)
session.add(sub_category13)
session.commit()

sub_category14 = SubCategory(user_id=1, name='Fashion Accessories', picture='https://www.shopolux.com/wp-content/uploads/2017/08/Megir-Quartz-Watch-Black-Men-Watches-2017-Luxury-Brand-Chronograph-Watches-Men-Clock-Stainless-Steel-Men.jpg',  # noqa
                                                         category=category1)
session.add(sub_category14)
session.commit()


# Category Women

category2 = Category(name='Women', picture='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTioqHgTCKKwu5SAr6LOe4h_vg3JnuAGbmhgZaQgCPlRKiDndvZFg',  # noqa
                                         user_id=1)
session.add(category2)
session.commit()

# Add Subcategories TopWear, BottomWear, Footwear, Fashion Accessories to Women
sub_category21 = SubCategory(user_id=1, name='TopWear', picture='https://assets.myntassets.com/h_240,q_90,w_180/v1/assets/images/1848639/2017/8/22/11503377901552-Roadster-Women-Navy-Blue-Regular-Fit-Solid-Casual-Shirt-1931503377901187-1_mini.jpg',  # noqa
                                                         category=category2)
session.add(sub_category21)
session.commit()

# Add items
dress1 = Items(name='FLoral Prom Dress', picture='https://image.dhgate.com/0x0/f2/albu/g5/M01/39/88/rBVaI1h0k7OAfp6fAAUMIOSzJow917.jpg',  # noqa
                           price="$100", user_id=1, seller_name='Shruti',
                           seller_phoneno='8699609577', rating=5,
                           category=category2, sub_category=sub_category21)
session.add(dress1)
session.commit()

dress2 = Items(name='Cut Bell Sleeves Top', picture='https://img.faballey.com/images/Product/TOP03399Z/d3.jpg',  # noqa
                           price="$100", user_id=1, seller_name='Shruti',
                           seller_phoneno='8699609577', rating=5,
                           category=category2, sub_category=sub_category21)
session.add(dress2)
session.commit()

sub_category22 = SubCategory(user_id=1, name='BottomWear', picture='http://picture-cdn.wheretoget.it/via91b-i.jpg',  # noqa
                                                         category=category2)
session.add(sub_category22)
session.commit()

sub_category23 = SubCategory(user_id=1, name='FootWear', picture='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRqbjuFy5tEbvKHG2XRRQLruQsSaz1tGHFlkjMCMHMPk84Io6ma',  # noqa
                                                         category=category2)
session.add(sub_category23)
session.commit()

sub_category24 = SubCategory(user_id=1, name='Fashion Accessories', picture='https://i.pinimg.com/736x/ee/3b/fd/ee3bfd383403df92d0f7d4abdb832029--retro-sunglasses-sunglasses-women.jpg',  # noqa
                                                         category=category2)
session.add(sub_category24)
session.commit()


# Category Kids

category3 = Category(name='Kids', picture='https://i.pinimg.com/736x/44/6b/3b/446b3bb7f75d548933759f24f00987cb--boys-and-girls-baby-outfit-for-girls.jpg', user_id=1)  # noqa
session.add(category3)
session.commit()

# Add Subcategories TopWear, BottomWear, Footwear, Fashion Accessories to Kids
sub_category31 = SubCategory(user_id=1, name='Clothing', picture='https://static1.squarespace.com/static/56665534e0327c2f0c83d310/56c5758fb6aa608778878d86/56c575908a65e29feeacaa1b/1455781556353/IMG_2165.jpg',  # noqa
                                                         category=category3)
session.add(sub_category31)
session.commit()

# Add items
dress1 = Items(name='Blue Princess Dress', picture='https://ae01.alicdn.com/kf/HTB1.3zsKpXXXXXQXFXXq6xXFXXX0/2016-European-and-American-style-dress-kids-girls-spring-and-summer-baby-girls-princess-dress-upscale.jpg',  # noqa
                           price="$100", user_id=1, seller_name='Shruti',
                           seller_phoneno='8699609577', rating=5,
                           category=category3, sub_category=sub_category31)
session.add(dress1)
session.commit()

dress2 = Items(name='Knit Sweater', picture='https://image.dhgate.com/albu_831465056_00/temp2.0x0.jpg',  # noqa
                           price="$100", user_id=1, seller_name='Shruti',
                           seller_phoneno='8699609577', rating=5,
                           category=category3, sub_category=sub_category31)
session.add(dress2)
session.commit()

sub_category32 = SubCategory(user_id=1, name='FootWear', picture='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTbP3Z48KIrFFvENz7hT4g_1smnYKWqb1sgUuVWnH6qf4lqef6p',  # noqa
                                                         category=category3)
session.add(sub_category32)
session.commit()

sub_category33 = SubCategory(user_id=1, name='Fashion Accessories', picture='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTDap1pFt8wZs8vn9vA1BVaNvL6_as7FZWNW716CvXCcVkjr9W8qg',  # noqa
                                                         category=category3)
session.add(sub_category33)
session.commit()

# Category Electrical Appliances

category4 = Category(name='Electrical Appliances', picture='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRsh4duSuSb_nEPoWqBRnU3a1hJIRdWG4zS32KqCW93mnl5mAyH',  # noqa
                                         user_id=1)
session.add(category4)
session.commit()

# Add Subcategories  Home Appliances to Electrical Appliances
sub_category41 = SubCategory(user_id=1, name='Home Appliances', picture='http://www.homeappliancesworld.com/files/2016/10/HA.jpg',  # noqa
                                                         category=category4)
session.add(sub_category41)
session.commit()

# Add items
item1 = Items(name='Red Color Kettle', picture='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTpLk__J_--vEe8STUUhwv-QQSGiWDZ0CAftsK0297UaYZb1BLOEA',  # noqa
                           price="$100", user_id=1, seller_name='Shruti',
                           seller_phoneno='8699609577', rating=5,
                           category=category4, sub_category=sub_category41)
session.add(item1)
session.commit()

print("Added all data")
