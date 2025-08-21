(function(){
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const $ = (id)=>document.getElementById(id);
    const startBtn = $('startBtn');
    const stopBtn = $('stopBtn');
    const statusEl = $('status');
    const transcriptEl = $('transcript');
    const goResultsBtn = $('goResults');
    const callApiBtn = $('callApi');
    const apiResultsEl = $('apiResults');
  
    if (!SR) {
      alert('이 브라우저는 음성 인식을 지원하지 않습니다. (Chrome 권장)');
      startBtn.disabled = true; stopBtn.disabled = true;
      return;
    }
  
    const TIME_LIMIT_SEC = 6;   // 최대 청취 시간
    let recognition = new SR();
    recognition.lang = 'ko-KR';
    recognition.interimResults = true;
    recognition.continuous = false;
    recognition.maxAlternatives = 1;
  
    let stopper = null;
    let finalText = '';
  
    function setStatus(t){ statusEl.textContent = t; }
  
    recognition.onstart = () => {
      finalText = '';
      transcriptEl.textContent = '인식 중…';
      setStatus('녹음 중');
      clearTimeout(stopper);
      stopper = setTimeout(()=>recognition.stop(), TIME_LIMIT_SEC * 1000);
    };
  
    recognition.onerror = (e) => {
      setStatus('오류');
      transcriptEl.textContent = '인식 오류: ' + (e.error || 'unknown');
      console.error(e);
    };
  
    recognition.onend = () => {
      setStatus('대기 중');
      clearTimeout(stopper);
    };
  
    recognition.onresult = (evt) => {
      let interim = '';
      for (let i = evt.resultIndex; i < evt.results.length; i++) {
        const chunk = evt.results[i][0].transcript;
        if (evt.results[i].isFinal) finalText += chunk;
        else interim += chunk;
      }
      const shown = (finalText || interim).trim();
      transcriptEl.textContent = shown || '인식 실패';
    };
  
    startBtn.onclick = () => recognition.start();
    stopBtn.onclick  = () => recognition.stop();
  
    // 1) 결과 페이지로 이동(타자 검색과 동일 로직)
    goResultsBtn.onclick = () => {
      const text = (finalText || transcriptEl.textContent || '').trim();
      if (!text) return alert('텍스트가 없습니다.');
      const url = (window.__RESULTS_URL__ || '/restaurants/results/')
        + '?q=' + encodeURIComponent(text) + '&source=voice';
      location.href = url;
    };
  
    // 2) 같은 페이지에서 API 호출 테스트(JSON)
    callApiBtn.onclick = async () => {
      const text = (finalText || transcriptEl.textContent || '').trim();
      if (!text) return alert('텍스트가 없습니다.');
  
      apiResultsEl.textContent = '검색 중…';
  
      // CSRF 토큰 (DRF SessionAuth를 쓰면 필요할 수 있음)
      const getCookie = (name) => {
        const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return m ? m.pop() : '';
      };
      const csrf = getCookie('csrftoken');
  
      try {
        const res = await fetch(window.__SEARCH_API__ || '/restaurants/api/search', {
          method: 'POST',
          headers: {
            'Content-Type':'application/json',
            'Accept':'application/json',
            'X-CSRFToken': csrf
          },
          body: JSON.stringify({ text, limit: 10 })
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        apiResultsEl.innerHTML = (data.cards || []).map(c => (
          `<div>🍽️ ${c.menu_name} · ₩${c.price ?? '-'} · [${c.restaurant_name}]</div>`
        )).join('') || '<div class="muted">결과 없음</div>';
      } catch (e) {
        console.error(e);
        apiResultsEl.textContent = '오류: ' + e.message;
      }
    };
  })();
  