  const form=document.getElementById("chatForm");
        const input= document.getElementById("userInput");
        const messages=document.getElementById("messages");
        form.addEventListener("submit",async (e)=>{
            e.preventDefault();
            const text= input.value.trim();
            if(!text)return;
            messages.innerHTML+=`<div class="msg user">tu:${text}</div>`;
            input.value="";
            const response = await fetch("/chat",{
                method:"POST",
                headers:{"Content-Type":"application/x-www-form-urlencoded"},
                body:`message=${encodeURIComponent(text)}`

            })
            const data = await response.json();
            messages.innerHTML+=`<div class="msg bot">bot:${data.response}</div>`;
            messages.scrollTop=messages.scrollHeight;

            
            
        })
  