import random
from app import create_app
from database import db
from models import User, Product, Cart, Order, OrderItem, Payment

app = create_app()

products_data = [
    # --- VEGETABLES ---
    {
        "name": "Fresh Organic Spinach",
        "description": "Crisp, iron-rich farm spinach leaves harvested fresh daily.",
        "cost": 150.00,
        "category": "VEGETABLES",
        "image_url": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&q=80&w=400",
        "stock": 45
    },
    {
        "name": "Ripe Red Tomatoes",
        "description": "Vine-ripened organic tomatoes packed with rich flavor and lycopene.",
        "cost": 100.00,
        "category": "VEGETABLES",
        "image_url": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&q=80&w=400",
        "stock": 60
    },
    {
        "name": "Organic Hass Avocados",
        "description": "Creamy, nutrient-dense avocados perfect for salads and toast.",
        "cost": 180.00,
        "category": "VEGETABLES",
        "image_url": "https://images.unsplash.com/photo-1523049673857-eb18f1d7b578?auto=format&fit=crop&q=80&w=400",
        "stock": 30
    },
    {
        "name": "Fresh Broccoli Crowns",
        "description": "Crisp green broccoli heads, high in fiber and essential vitamins.",
        "cost": 160.00,
        "category": "VEGETABLES",
        "image_url": "https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&fit=crop&q=80&w=400",
        "stock": 25
    },
    {
        "name": "Crunchy Sweet Carrots",
        "description": "Farm-fresh organic carrots loaded with beta-carotene.",
        "cost": 110.00,
        "category": "VEGETABLES",
        "image_url": "https://images.unsplash.com/photo-1598170845058-12ef4a457939?auto=format&fit=crop&q=80&w=400",
        "stock": 50
    },

    # --- FRUITS ---
    {
        "name": "Organic Honeycrisp Apples",
        "description": "Sweet, juicy, and crunchy highland apples grown without pesticides.",
        "cost": 280.00,
        "category": "FRUITS",
        "image_url": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&q=80&w=400",
        "stock": 40
    },
    {
        "name": "Sweet Tropical Bananas",
        "description": "Naturally ripened yellow banana cluster, packed with potassium.",
        "cost": 90.00,
        "category": "FRUITS",
        "image_url": "https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&q=80&w=400",
        "stock": 75
    },
    {
        "name": "Fresh Blueberries (250g)",
        "description": "Plump and juicy antioxidant-rich blueberries, perfect for snacking.",
        "cost": 350.00,
        "category": "FRUITS",
        "image_url": "https://images.unsplash.com/photo-1498557850523-fd3d118b962e?auto=format&fit=crop&q=80&w=400",
        "stock": 8  # Low stock
    },
    {
        "name": "Juicy Seedless Watermelon",
        "description": "Refreshing and naturally sweet whole watermelon harvested at peak ripeness.",
        "cost": 400.00,
        "category": "FRUITS",
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&q=80&w=400",
        "stock": 15
    },
    {
        "name": "Fresh Sweet Strawberries",
        "description": "Bright red, fragrant strawberries packed with Vitamin C.",
        "cost": 300.00,
        "category": "FRUITS",
        "image_url": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&q=80&w=400",
        "stock": 5  # Low stock
    },

    # --- DAIRY & EGGS ---
    {
        "name": "Farm Fresh Whole Milk (1L)",
        "description": "Pure pasteurized whole milk direct from pasture-fed dairy cattle.",
        "cost": 120.00,
        "category": "DAIRY",
        "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?auto=format&fit=crop&q=80&w=400",
        "stock": 35
    },
    {
        "name": "Free-Range Large Eggs (12pk)",
        "description": "Rich golden-yolk eggs laid by pasture-raised hens.",
        "cost": 320.00,
        "category": "DAIRY",
        "image_url": "https://images.unsplash.com/photo-1516448620398-c5f44bf9f441?auto=format&fit=crop&q=80&w=400",
        "stock": 20
    },
    {
        "name": "Organic Greek Yogurt (500g)",
        "description": "Thick, creamy plain Greek yogurt packed with gut-healthy probiotics.",
        "cost": 270.00,
        "category": "DAIRY",
        "image_url": "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&q=80&w=400",
        "stock": 18
    },
    {
        "name": "Artisanal Cheddar Cheese",
        "description": "Aged sharp cheddar cheese block crafted from pasteurized cow's milk.",
        "cost": 450.00,
        "category": "DAIRY",
        "image_url": "https://images.unsplash.com/photo-1618160702438-9b02ab6515c9?auto=format&fit=crop&q=80&w=400",
        "stock": 12
    },
    {
        "name": "Grass-Fed Unsalted Butter",
        "description": "Rich, churned cream butter perfect for cooking and baking.",
        "cost": 310.00,
        "category": "DAIRY",
        "image_url": "https://images.unsplash.com/photo-1589985270826-4b7bb135bc9d?auto=format&fit=crop&q=80&w=400",
        "stock": 6  # Low stock
    },

    # --- BAKERY ---
    {
        "name": "Artisanal Sourdough Bread",
        "description": "Slow-fermented crusty sourdough loaf baked with organic wheat flour.",
        "cost": 220.00,
        "category": "BAKERY",
        "image_url": "https://images.unsplash.com/photo-1585478259715-876a6a81fc08?auto=format&fit=crop&q=80&w=400",
        "stock": 15
    },
    {
        "name": "Whole Grain Croissants (4pk)",
        "description": "Flaky butter croissants made with whole wheat flour.",
        "cost": 260.00,
        "category": "BAKERY",
        "image_url": "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&q=80&w=400",
        "stock": 9  # Low stock
    },
    {
        "name": "Whole Wheat Sandwich Bread",
        "description": "Soft, high-fiber whole grain bread baked fresh daily.",
        "cost": 180.00,
        "category": "BAKERY",
        "image_url": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&q=80&w=400",
        "stock": 28
    },
    {
        "name": "Fresh Blueberry Muffins (4pk)",
        "description": "Moist, oven-baked bakery muffins packed with fresh berries.",
        "cost": 240.00,
        "category": "BAKERY",
        "image_url": "https://images.unsplash.com/photo-1607958996333-41aef7caefaa?auto=format&fit=crop&q=80&w=400",
        "stock": 7  # Low stock
    },

    # --- PANTRY STAPLES ---
    {
        "name": "Extra Virgin Olive Oil (500ml)",
        "description": "Cold-pressed extra virgin olive oil from Mediterranean olives.",
        "cost": 850.00,
        "category": "PANTRY",
        "image_url": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&q=80&w=400",
        "stock": 14
    },
    {
        "name": "Organic Jasmine Rice (2kg)",
        "description": "Long-grain aromatic jasmine rice, ideal for daily meals.",
        "cost": 520.00,
        "category": "PANTRY",
        "image_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&q=80&w=400",
        "stock": 30
    },
    {
        "name": "Raw Wildflower Honey (500g)",
        "description": "Unfiltered pure honey rich in natural enzymes and antioxidants.",
        "cost": 650.00,
        "category": "PANTRY",
        "image_url": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&q=80&w=400",
        "stock": 22
    },
    {
        "name": "Whole Grain Oats (1kg)",
        "description": "100% whole grain rolled oats for hearty breakfasts and baking.",
        "cost": 290.00,
        "category": "PANTRY",
        "image_url": "https://images.unsplash.com/photo-1517673400267-0251440c45dc?auto=format&fit=crop&q=80&w=400",
        "stock": 25
    },
    {
        "name": "Pink Himalayan Sea Salt (250g)",
        "description": "Unrefined mineral-rich crystal salt for cooking and seasoning.",
        "cost": 210.00,
        "category": "PANTRY",
        "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?auto=format&fit=crop&q=80&w=400",
        "stock": 40
    },

    # --- BEVERAGES ---
    {
        "name": "Fresh Orange Juice (1L)",
        "description": "Cold-pressed 100% natural Valencia orange juice with pulp.",
        "cost": 250.00,
        "category": "BEVERAGES",
        "image_url": "https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?auto=format&fit=crop&q=80&w=400",
        "stock": 20
    },
    {
        "name": "Dark Roast Coffee Beans (500g)",
        "description": "Single-origin Arabica coffee beans roasted for a deep, bold flavor.",
        "cost": 750.00,
        "category": "BEVERAGES",
        "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&q=80&w=400",
        "stock": 18
    },
    {
        "name": "Organic Green Tea Bags (20pk)",
        "description": "Refreshing herbal green tea leaves sourced from organic tea gardens.",
        "cost": 320.00,
        "category": "BEVERAGES",
        "image_url": "https://images.unsplash.com/photo-1597481499750-3e6b22637e12?auto=format&fit=crop&q=80&w=400",
        "stock": 30
    },
    {
        "name": "Sparkling Mineral Water (1L)",
        "description": "Naturally carbonated mineral water sourced from mountain springs.",
        "cost": 140.00,
        "category": "BEVERAGES",
        "image_url": "https://images.unsplash.com/photo-1560023907-5f339617ea30?auto=format&fit=crop&q=80&w=400",
        "stock": 35
    },
    {
        "name": "Pure Coconut Water (500ml)",
        "description": "100% natural hydration packed with electrolytes.",
        "cost": 190.00,
        "category": "BEVERAGES",
        "image_url": "https://images.unsplash.com/photo-1525385133512-2f3bdd039054?auto=format&fit=crop&q=80&w=400",
        "stock": 4  # Low stock
    }
]


def seed_database():
    with app.app_context():
        print("Resetting database tables...")
        db.drop_all()
        db.create_all()

        print("Seeding Users...")
        super_admin = User(
            username="superadmin",
            email="superadmin@sokocommerce.com",
            phone="254700000001",
            is_admin=True,
            role="SUPER_ADMIN"
        )
        super_admin.set_password("SuperAdmin123!")

        admin = User(
            username="admin",
            email="admin@sokocommerce.com",
            phone="254700000002",
            is_admin=True,
            role="ADMIN"
        )
        admin.set_password("AdminPass123!")

        customer = User(
            username="johndoe",
            email="johndoe@example.com",
            phone="254712345678",
            is_admin=False,
            role="USER"
        )
        customer.set_password("UserPass123!")

        db.session.add_all([super_admin, admin, customer])
        db.session.commit()

        # Initialize Customer Cart
        db.session.add(Cart(user_id=customer.id))

        print(f"Seeding {len(products_data)} grocery products...")
        created_products = []
        for prod in products_data:
            new_prod = Product(
                name=prod["name"],
                description=prod["description"],
                cost=prod["cost"],
                stock=prod.get("stock", 20),
                category=prod["category"],
                image_url=prod["image_url"]
            )
            db.session.add(new_prod)
            created_products.append(new_prod)

        db.session.commit()

        print("Seeding Sample Order & Payment...")
        # Grab two products for a sample order
        sample_prod1 = created_products[0]  # Spinach (150.00)
        sample_prod2 = created_products[10] # Milk (120.00)
        total_price = (sample_prod1.cost * 2) + sample_prod2.cost

        sample_order = Order(
            user_id=customer.id,
            total_amount=total_price,
            status="PAID",
            tracking_number="SKC-1092834",
            carrier="Local Courier"
        )
        db.session.add(sample_order)
        db.session.commit()

        item_1 = OrderItem(
            order_id=sample_order.id,
            product_id=sample_prod1.id,
            quantity=2,
            price=sample_prod1.cost
        )
        item_2 = OrderItem(
            order_id=sample_order.id,
            product_id=sample_prod2.id,
            quantity=1,
            price=sample_prod2.cost
        )

        payment_record = Payment(
            user_id=customer.id,
            order_id=sample_order.id,
            checkout_request_id="ws_CO_21082026_15000099",
            merchant_request_id="29115-3462711-9",
            phone_number=customer.phone,
            amount=total_price,
            mpesa_receipt_number="RGH9182302",
            status="COMPLETED",
            result_desc="The service request has been processed successfully."
        )

        db.session.add_all([item_1, item_2, payment_record])
        db.session.commit()

        print("Database successfully seeded!")
        print("-" * 50)
        print("Default Accounts:")
        print("  Super Admin : superadmin / SuperAdmin123!")
        print("  Admin       : admin      / AdminPass123!")
        print("  Customer    : johndoe    / UserPass123!")
        print("-" * 50)


if __name__ == "__main__":
    seed_database()