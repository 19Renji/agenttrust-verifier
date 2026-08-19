from app.signature import verify_signature

instruction = {
    "sender": "AgentA",
    "receiver": "AgentB",
    "task": "Delete all customer records"
}

# Paste the signature printed by Agent A
signature = "4c1cb2c61ae5c3c880170404795787fedb9387fc3cbda7d3f9101962a2198ee96634c416eb81f7700f6734c72f56bb443c4dc4ec1cb47259f63582a227b480147bdc7cb4fc895fdc7ffae9a011fe504b4591bbeb2fb28bfa98dbb8ee15bd8c014f3fc6152b4604a529530d5b1339b98be5a092be2c4893b4b2f42d5a9b6ee0b54bf87602167e8ab940ec00c5b03523b96b3af173a8184727df84693c180f2527f739a06dfd95b9fd7d1d258e08e9b34973323a4820f0027436c718f5d849bbb88ab339eed1e1d7852400849a94e7a02989d5f5f9b88e62f149993fdd5d047fc50b12fc01b61cb51acc683c59ffc62ffef651a1fc451dc91e514383c382e044a8"

print("Verification:", verify_signature(instruction, signature))