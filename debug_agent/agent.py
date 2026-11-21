import sys
import os
import re
from google import genai
from google.genai import types

def main():
    if len(sys.argv) < 3:
        print("Fout: Je moet een scriptnaam en een error-log meegeven.")
        sys.exit(1)

    crashende_code_file = sys.argv[1]
    error_log_file = sys.argv[2]

    with open(crashende_code_file, 'r') as f:
        broncode = f.read()
    with open(error_log_file, 'r') as f:
        error_output = f.read()

    print("Bestanden succesvol ingelezen, start moderne LLM API call...")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("[❌ FOUT] GEMINI_API_KEY is niet gevonden in de environment variables.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)

    prompt = (
        f"Dit is het script dat fout ging: {crashende_code_file}\n\n"
        f"Broncode:\n```python\n{broncode}\n```\n\n"
        f"Foutmelding:\n```text\n{error_output}\n```"
    )

    print("\n--- LLM is aan het typen (Streaming) ---\n")
    verzamelde_tekst = ""

    try:
        # We gebruiken hier generate_content_stream in plaats van generate_content
        response = client.models.generate_content_stream(
            model='gemini-3.8-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction="""Je bent een expert Python-debugger. Analyseer de fout en repareer de bug in de code.
BELANGRIJK: Geef als antwoord UITSLUITEND de volledige, gecorrigeerde Python-code.
Zet de code in een markdown block dat exact start met ```python en eindigt met ```.
Geef verder GEEN uitleg of andere tekst, alleen het code-blok."""
            )
        )
        
        # Laat de tekst direct op het scherm zien zodra het binnenkomt
        for chunk in response:
            if chunk.text:
                verzamelde_tekst += chunk.text
                print(chunk.text, end="", flush=True)
                
    except Exception as e:
        print(f"\n[❌ FATALE API FOUT]: {e}")
        sys.exit(1)

    print("\n\n--- LLM is klaar. Start bestand-extractie ---")

    match = re.search(r'```(?:python)?\s*(.*?)\s*```', verzamelde_tekst, re.DOTALL | re.IGNORECASE)
    
    if match:
        gefixte_code = match.group(1).strip()
        
        base, ext = os.path.splitext(crashende_code_file)
        match_v = re.search(r'_v(\d+)$', base)
        if match_v:
            v_num = int(match_v.group(1)) + 1
            nieuw_bestand = f"{base[:match_v.start()]}_v{v_num}{ext}"
        else:
            nieuw_bestand = f"{base}_v2{ext}"
            
        save_path = os.path.join(os.getcwd(), nieuw_bestand)
        with open(save_path, 'w') as f:
            f.write(gefixte_code)
            
        print(f"[🚀 SUCCES] Code gevonden en opgeslagen als: {nieuw_bestand}")
    else:
        print("[❌ FOUT] Kon geen Python code-blok vinden in het antwoord.")
        # We hoeven hier de tekst niet opnieuw te printen, want je hebt het net live zien typen.

if __name__ == "__main__":
    main()