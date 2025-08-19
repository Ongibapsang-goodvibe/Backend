function VoiceButton({ initialLabel }) {
    const [listening, setListening] = React.useState(false);
    const [text, setText] = React.useState("");
  
    const start = () => {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) {
        alert("이 브라우저는 음성 인식을 지원하지 않아요.");
        return;
      }
      const rec = new SR();
      rec.lang = "ko-KR";
      rec.interimResults = true;
      rec.onresult = (e) => {
        const t = Array.from(e.results).map(r => r[0].transcript).join("");
        setText(t);
      };
      rec.onend = () => setListening(false);
      rec.start();
      setListening(true);
    };
  
    const submit = async () => {
      await fetch("/api/delivery/logs/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          initial_label: initialLabel, // "네" 또는 "문제가 있어요"
          text,                        // 음성 인식 결과
          source: "VOICE"
        })
      });
      // 완료 화면 이동 등
    };
  
    return (
      <>
        <button onClick={start} disabled={listening}>🎤 말로 할게요</button>
        {text && <button onClick={submit}>선택완료</button>}
      </>
    );
  }
  