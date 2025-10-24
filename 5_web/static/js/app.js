let currentErrors = [];
let checkInProgress = false;
let checkTimeout;
let currentErrorElement = null;

function checkText() {
    if (checkInProgress) {
        return;
    }
    
    const text = document.getElementById('editableText').textContent.trim();
    if (!text) {
        return;
    }
    
    checkInProgress = true;
    showLoading();
    
    fetch('/check', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('სერვერის შეცდომა: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        hideLoading();
        checkInProgress = false;
        
        if (data.error) {
            console.error('შეცდომა:', data.error);
            return;
        }
        
        currentErrors = data.errors || [];
        highlightErrors(currentErrors);
    })
    .catch(error => {
        hideLoading();
        checkInProgress = false;
        console.error('შეცდომა ტექსტის შემოწმებისას:', error);
    });
}

function highlightErrors(errors) {
    const editableText = document.getElementById('editableText');
    let content = editableText.innerHTML;
    
    // წინა მონიშვნების წაშლა
    content = content.replace(/<span class="spelling-error"[^>]*>([^<]*)<\/span>/g, '$1');
    
    errors.forEach(error => {
        const errorRegex = new RegExp(escapeRegExp(error.word), 'g');
        content = content.replace(errorRegex, 
            `<span class="spelling-error" data-word="${escapeHtml(error.word)}" data-suggestions="${escapeHtml(JSON.stringify(error.suggestions))}">${error.word}</span>`
        );
    });
    
    editableText.innerHTML = content;
    
    // დაამატე event listeners შეცდომებზე
    document.querySelectorAll('.spelling-error').forEach(element => {
        element.addEventListener('click', handleErrorClick);
    });
    
    // Автоматически подстраиваем высоту текстового поля
    autoResizeTextarea();
}

function handleErrorClick(event) {
    const element = event.currentTarget;
    const word = element.getAttribute('data-word');
    const suggestions = JSON.parse(element.getAttribute('data-suggestions') || '[]');
    
    showContextMenu(element, word, suggestions);
    event.stopPropagation();
}

function showContextMenu(element, word, suggestions) {
    hideContextMenu();
    
    currentErrorElement = element;
    const menu = document.getElementById('contextMenu');
    const errorWord = document.getElementById('errorWord');
    const suggestionsList = document.getElementById('suggestionsList');
    
    errorWord.textContent = word;
    
    if (suggestions && suggestions.length > 0) {
        suggestionsList.innerHTML = suggestions.map(suggestion => 
            `<div class="suggestion-item" onclick="replaceWord('${escapeString(suggestion)}')">${suggestion}</div>`
        ).join('');
    } else {
        suggestionsList.innerHTML = '<div class="no-suggestions">არ იძებნება</div>';
    }
    
    // პოზიციის განსაზღვრა
    const rect = element.getBoundingClientRect();
    const menuRect = menu.getBoundingClientRect();
    
    let left = rect.left;
    let top = rect.bottom + 5;
    
    // Проверяем, чтобы меню не выходило за правый край экрана
    if (left + menuRect.width > window.innerWidth) {
        left = window.innerWidth - menuRect.width - 10;
    }
    
    // Проверяем, чтобы меню не выходило за нижний край экрана
    if (top + menuRect.height > window.innerHeight) {
        top = rect.top - menuRect.height - 5;
    }
    
    menu.style.left = left + 'px';
    menu.style.top = top + 'px';
    menu.style.display = 'block';
    
    // დაამატე event listener დოკუმენტზე მენიუს დასახურებლად
    setTimeout(() => {
        document.addEventListener('click', hideContextMenuOnClick);
    }, 100);
}

function hideContextMenu() {
    const menu = document.getElementById('contextMenu');
    menu.style.display = 'none';
    currentErrorElement = null;
    document.removeEventListener('click', hideContextMenuOnClick);
}

function hideContextMenuOnClick(event) {
    const menu = document.getElementById('contextMenu');
    if (!menu.contains(event.target)) {
        hideContextMenu();
    }
}

function replaceWord(newWord) {
    if (!currentErrorElement) return;
    
    const oldWord = currentErrorElement.getAttribute('data-word');
    currentErrorElement.outerHTML = newWord;
    
    hideContextMenu();
    
    // განაახლე ტექსტი და ხელახლა შეამოწმე
    setTimeout(() => {
        checkText();
    }, 100);
}

function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Автоматическое изменение размера текстового поля
function autoResizeTextarea() {
    const editableText = document.getElementById('editableText');
    // Сбрасываем высоту чтобы получить правильный scrollHeight
    editableText.style.height = 'auto';
    // Устанавливаем высоту равной scrollHeight
    editableText.style.height = editableText.scrollHeight + 'px';
}

// დამხმარე ფუნქციები
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function escapeString(text) {
    return text.replace(/'/g, "\\'");
}

function escapeRegExp(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ავტომატური შემოწმება ტაიმაუთით
function scheduleCheck() {
    clearTimeout(checkTimeout);
    checkTimeout = setTimeout(checkText, 1000);
}

// ინიციალიზაცია
document.addEventListener('DOMContentLoaded', function() {
    const editableText = document.getElementById('editableText');
    
    editableText.addEventListener('input', function() {
        // Автоматически меняем размер поля
        autoResizeTextarea();
        
        // Автоматическая проверка орфографии
        scheduleCheck();
    });
    
    editableText.addEventListener('paste', function(e) {
        e.preventDefault();
        const text = (e.clipboardData || window.clipboardData).getData('text');
        document.execCommand('insertText', false, text);
        
        // Автоматически меняем размер и проверяем
        setTimeout(() => {
            autoResizeTextarea();
            checkText();
        }, 100);
    });
    
    // Автоматическое изменение размера при загрузке
    setTimeout(autoResizeTextarea, 100);
    
    // დაამატე ტექსტის მაგალითი თუ ცარიელია
    if (!editableText.textContent.trim()) {
        setTimeout(() => {
            const exampleText = "გამარჯობა, როგორ ხარ? ეს არის სატესტო ტექსტი ქართული მართლწერის შემოწმებისთვის. პროგრამა ამოწმებს ტექსტს და პოულობს შეცდომებს.";
            editableText.innerHTML = exampleText;
            autoResizeTextarea();
            setTimeout(checkText, 500);
        }, 1000);
    }
});

// Обработка изменения размера окна
window.addEventListener('resize', function() {
    autoResizeTextarea();
});