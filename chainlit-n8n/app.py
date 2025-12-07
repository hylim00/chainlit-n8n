import chainlit as cl
import aiohttp
import os
import logging

logging.basicConfig(level=logging.DEBUG)

# ================================================================
# 🔐 PASSWORD AUTHENTICATION (WAJIB UNTUK LOGIN & HISTORY)
# ================================================================
@cl.password_auth_callback
def auth_callback(email: str, password: str):
    if email == "admin@k3app.com" and password == "admin123":
        return cl.User(identifier=email)
    return None


# ================================================================
# WEBHOOK URLS
# ================================================================
N8N_WEBHOOK_TEXT = "http://localhost:5678/webhook-test/chainlit"
N8N_WEBHOOK_UPLOAD = "http://localhost:5678/webhook-test/upload-file"


# ================================================================
# STARTER BUTTON (Tanya K3 & Lapor SAC)
# ================================================================
@cl.set_starters
async def starters():
    return [
        cl.Starter(
            label="Tanya K3",
            message="ask_k3",
            icon="/public/phone.svg"
        ),
        cl.Starter(
            label="Lapor SAC",
            message="lapor_sac",
            icon="/public/alert.svg"
        ),
    ]


# ================================================================
# STATE MANAGEMENT
# ================================================================
def get_user_stage():
    return cl.user_session.get("stage", "greeting")

def set_user_stage(stage: str):
    cl.user_session.set("stage", stage)


# ================================================================
# MAIN MESSAGE HANDLER
# ================================================================
@cl.on_message
async def on_message(message: cl.Message):

    user_id = message.id
    stage = get_user_stage()

    print("\n==============================")
    print("📩 NEW MESSAGE RECEIVED")
    print("==============================")
    print("Message ID:", user_id)
    print("Content:", message.content)
    print("Stage BEFORE:", stage)
    print("==============================\n")

    normalized_msg = message.content.lower().strip()

    # ============================================================
    # STARTER BUTTON LOGIC
    # ============================================================
    if normalized_msg == "ask_k3":
        print("Starter ASK K3 triggered")
        set_user_stage("ask_k3")
        stage = "ask_k3"

    if normalized_msg == "lapor_sac":
        print("Starter LAPOR SAC triggered")
        set_user_stage("lapor_sac")
        stage = "lapor_sac"


    # ============================================================
    # FILE UPLOAD HANDLING
    # ============================================================
    if message.elements:
        print("File upload detected...")

        for element in message.elements:
            file_path = getattr(element, "path", None)

            if not file_path or not os.path.exists(file_path):
                print("❌ Invalid file path.")
                continue

            filename = os.path.basename(file_path)
            mime_type = getattr(element, "mime_type", "application/octet-stream")

            print("\n------ FILE INFO ------")
            print("Filename:", filename)
            print("MIME:", mime_type)
            print("Path:", file_path)

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            form = aiohttp.FormData()
            form.add_field("stage", stage)
            form.add_field("message", message.content or "")
            form.add_field("file", file_bytes, filename=filename, content_type=mime_type)

            print("\n🌐 Sending FILE to:", N8N_WEBHOOK_UPLOAD)

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(N8N_WEBHOOK_UPLOAD, data=form) as resp:
                        print("📡 Upload webhook status:", resp.status)

                        try:
                            data = await resp.json()
                            print("📨 JSON response:", data)
                            reply = data.get("reply", f"File {filename} uploaded.")
                            set_user_stage(data.get("next_stage", stage))
                        except:
                            txt = await resp.text()
                            print("📨 TEXT response:", txt)
                            reply = f"File '{filename}' uploaded."

                except Exception as e:
                    print("🔥 Upload error:", e)
                    reply = f"Upload failed: {e}"

            # === Avatar custom applied here ===
            await cl.Message(
                author="Asisten-K3",
                content=reply
            ).send()
            return


    # ============================================================
    # TEXT MESSAGE HANDLING → N8N WEBHOOK
    # ============================================================
    greetings = ["halo", "hai", "hi", "hello", "pagi", "siang", "sore", "malam"]

    if normalized_msg in greetings:
        set_user_stage("greeting")
        stage = "greeting"

    payload = {"message": message.content, "stage": stage}

    print("\n🌐 Sending TEXT to:", N8N_WEBHOOK_TEXT)
    print("Payload:", payload)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(N8N_WEBHOOK_TEXT, json=payload) as resp:
                print("📡 Text webhook status:", resp.status)

                try:
                    data = await resp.json()
                    print("📨 JSON:", data)
                    reply = data.get("reply", f"Message '{message.content}' delivered.")
                    set_user_stage(data.get("next_stage", stage))
                except:
                    txt = await resp.text()
                    print("📨 TEXT:", txt)
                    reply = f"Message sent (non-JSON)."

        except Exception as e:
            print("🔥 Error sending text:", e)
            reply = f"Webhook request failed: {e}"

    # === Avatar custom applied here too ===
    await cl.Message(
        author="Asisten-K3",
        content=reply
    ).send()
