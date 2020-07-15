db.createUser(
    {
        user: "admin",
        pwd: "test",
        roles: [
            {
                role: "readWrite",
                db: "career_crawler"
            }
        ]
    }
)
