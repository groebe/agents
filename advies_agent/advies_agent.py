import sys
import os
from google import genai
from google.genai import types

def main():
    if len(sys.argv) < 3:
        print("Fout: Je moet een scriptnaam en een succes-log meegeven.")
        sys.exit(1)

    succesvolle_code_file = sys.argv[1]
    succes_log_file = sys.argv[2]

    with open(succesvolle_code_file, 'r') as f:
        broncode = f.read()
    with open(succes_log_file, 'r') as f:
        succes_output = f.read()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[❌ FOUT] GEMINI_API_KEY is niet gevonden in de environment variables.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)

    prompt = (
        f"Hier is het Python script dat is uitgevoerd: {succesvolle_code_file}\n\n"
        f"Broncode ter context:\n```python\n{broncode}\n```\n\n"
        f"En hier is de succesvolle output van de berekening:\n```text\n{succes_output}\n```"
    )

    print("\n[🧠 ADVIES AGENT] Output analyseren (Streaming)...\n")

    try:
        response = client.models.generate_content_stream(
            model='gemini-3.8-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="""Je bent een senior wetenschappelijk adviseur (gespecialiseerd in computationele chemie, fysica en materialen zoals FeNi-kristallen). 
Je krijgt de broncode en de succesvolle output van een berekening.
Jouw taak:
1. Analyseer de uitkomsten (zoals energieën, spin-toestanden, of optimalisatie-stappen).
2. Geef een heldere, professionele interpretatie van wat deze resultaten betekenen.
3. Trek een conclusie of geef een aanbeveling voor een mogelijke vervolgstap in het onderzoek.
Spreek de gebruiker direct en professioneel aan. Geef GEEN code terug, alleen je analyse in heldere tekst."""
            )
        )
        
        for chunk in response:
            if chunk.text:
                print(chunk.text, end="", flush=True)
                
    except Exception as e:
        print(f"\n[❌ FATALE API FOUT]: {e}")
        sys.exit(1)

    print("\n\n--- [EINDE ADVIES] ---")

if __name__ == "__main__":
    main()
