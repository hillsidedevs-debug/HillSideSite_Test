from HillSide import create_app

app = create_app()

if __name__ == '__main__':
        # --- ADD THIS TEST BLOCK ---
    print("--- CONFIG CHECK ---")
    print(f"Public Key:  {app.config.get('RECAPTCHA_PUBLIC_KEY')}")
    print(f"Private Key: {app.config.get('RECAPTCHA_PRIVATE_KEY')}")
    print(f"Secret Key Set: {bool(app.config.get('SECRET_KEY'))}")
    print("---------------------")
    # ---------------------------
    app.run(debug=True)

    
