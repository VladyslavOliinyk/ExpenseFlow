"""
Seed script: creates users, categories, and sample claims.
Run: python -m app.seed
"""
from app.database import SessionLocal
from app.models import User, Category, Claim, ClaimStatus
from datetime import date


USERS = [
    {"name": "Alice Johnson", "email": "alice@company.com"},
    {"name": "Bob Smith", "email": "bob@company.com"},
    {"name": "Carol Davis", "email": "carol@company.com"},
    {"name": "Dan Lee", "email": "dan@company.com"},
    {"name": "Eve Martinez", "email": "eve@company.com"},
]

# Categories will be assigned responsible_manager after users are created
CATEGORIES = [
    {"name": "Office", "manager_email": "alice@company.com"},
    {"name": "Travel", "manager_email": "bob@company.com"},
    {"name": "Client Entertainment", "manager_email": "carol@company.com"},
    {"name": "Software/Subscriptions", "manager_email": "alice@company.com"},
    {"name": "Other", "manager_email": "dan@company.com"},
]


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already seeded, skipping.")
            return

        # Create users
        users = {}
        for u in USERS:
            user = User(name=u["name"], email=u["email"])
            db.add(user)
            db.flush()
            users[u["email"]] = user
            print(f"  Created user: {u['name']}")

        # Create categories
        categories = {}
        for c in CATEGORIES:
            manager = users[c["manager_email"]]
            category = Category(name=c["name"], responsible_manager_id=manager.id)
            db.add(category)
            db.flush()
            categories[c["name"]] = category
            print(f"  Created category: {c['name']} -> manager: {manager.name}")

        # Sample claims
        # NOTE: requester must never be the manager of the claim's category
        # Category managers: Office=Alice, Travel=Bob, Client Entertainment=Carol,
        #                    Software/Subscriptions=Alice, Other=Dan
        sample_claims = [
            {   # pending — Bob's Travel claim, but Carol is the requester (not Bob)
                "requester_email": "carol@company.com",
                "category": "Travel",
                "amount": "245.50",
                "description": "Flight to NYC for client meeting Q3",
                "expense_date": date(2026, 8, 15),
                "payment_details": "Bank transfer to Carol Davis, IBAN: GB29NWBK60161331926819",
                "status": ClaimStatus.pending,
            },
            {   # pending — Client Entertainment claim by Eve (manager is Carol)
                "requester_email": "eve@company.com",
                "category": "Client Entertainment",
                "amount": "320.00",
                "description": "Team dinner with Acme Corp executives after partnership signing",
                "expense_date": date(2026, 8, 20),
                "payment_details": "Reimburse to eve@company.com via PayPal",
                "status": ClaimStatus.pending,
            },
            {   # approved — Software/Subscriptions by Bob (manager is Alice)
                "requester_email": "bob@company.com",
                "category": "Software/Subscriptions",
                "amount": "49.99",
                "description": "Notion Pro annual subscription for project management",
                "expense_date": date(2026, 8, 1),
                "payment_details": "Corporate card ending 4242",
                "status": ClaimStatus.approved,
            },
            {   # rejected — Office claim by Eve (manager is Alice)
                "requester_email": "eve@company.com",
                "category": "Office",
                "amount": "89.00",
                "description": "Ergonomic mouse and keyboard for home office",
                "expense_date": date(2026, 7, 28),
                "payment_details": "Reimburse via bank: Eve Martinez, Sort: 20-00-00, Acc: 87654321",
                "status": ClaimStatus.rejected,
                "reject_comment": "Home office equipment requires separate approval form. Please resubmit with form HR-07.",
            },
            {   # pending — Travel claim by Dan (manager is Bob)
                "requester_email": "dan@company.com",
                "category": "Travel",
                "amount": "1200.00",
                "description": "Hotel accommodation for annual conference",
                "expense_date": date(2026, 8, 10),
                "payment_details": "Bank transfer to Dan Lee, Sort: 20-00-00, Acc: 11223344",
                "status": ClaimStatus.pending,
            },
        ]

        for sc in sample_claims:
            requester = users[sc["requester_email"]]
            category = categories[sc["category"]]
            claim = Claim(
                requester_id=requester.id,
                category_id=category.id,
                amount=sc["amount"],
                description=sc["description"],
                expense_date=sc["expense_date"],
                payment_details=sc["payment_details"],
                status=sc["status"],
                reject_comment=sc.get("reject_comment"),
            )
            db.add(claim)

        db.commit()
        print("\nSeed complete!")
        print("\nUser summary:")
        for email, user in users.items():
            managed = [c["name"] for c in CATEGORIES if c["manager_email"] == email]
            role = f"Manager of: {', '.join(managed)}" if managed else "Employee only"
            print(f"  [{user.id}] {user.name} ({email}) — {role}")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed()
