import os
try:
    from PIL import Image, ImageDraw
except ImportError:
    import subprocess
    subprocess.check_call(["python", "-m", "pip", "install", "pillow"])
    from PIL import Image, ImageDraw

os.makedirs("demos", exist_ok=True)

width, height = 800, 400
frames = []

base_text = "$ agent-cli chat --sync\n"
dialogue = [
    "> User: What guardrails are in place?",
    "> Agent [Thinking]: Decomposing query via PlannerNode...",
    "> Agent [Tool]:  web_search('security policies')",
    "> Agent [Guard]: Scrutinizing response through ToxicityFilter...",
    "> Agent [Response]: The agent uses PII scrubbing, prompt injection detectors, and token limits."
]

for i in range(len(dialogue) + 1):
    img = Image.new('RGB', (width, height), color=(30, 30, 30))
    d = ImageDraw.Draw(img)
    
    current_text = base_text + "\n\n".join(dialogue[:i])
    
    # Using default font which might be small but works for a mock
    d.text((20, 20), current_text, fill=(0, 255, 0))
    
    # Add frames to simulate time passing
    for _ in range(15):
        frames.append(img.copy())

frames[0].save('demos/demo.gif', save_all=True, append_images=frames[1:], duration=150, loop=0)
print("Successfully generated mock CLI GIF at demos/demo.gif")
