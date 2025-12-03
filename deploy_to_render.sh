#!/bin/bash

# 🚀 Render.com Deployment Script
# Telegram Panel'i Render'a deploy eder

echo "🚀 Telegram Panel - Render Deployment"
echo "======================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Git kontrolü
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git yüklü değil!${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Deployment Checklist${NC}"
echo ""

# 1. Git repository kontrolü
if [ -d .git ]; then
    echo -e "${GREEN}✅ Git repository mevcut${NC}"
else
    echo -e "${YELLOW}⚠️  Git repository yok, oluşturuluyor...${NC}"
    git init
    echo -e "${GREEN}✅ Git repository oluşturuldu${NC}"
fi

# 2. .gitignore kontrolü
if [ -f .gitignore ]; then
    echo -e "${GREEN}✅ .gitignore mevcut${NC}"
else
    echo -e "${RED}❌ .gitignore bulunamadı!${NC}"
    exit 1
fi

# 3. Requirements kontrolü
if [ -f web_panel/requirements.txt ] && [ -f requirements.txt ]; then
    echo -e "${GREEN}✅ Requirements dosyaları mevcut${NC}"
else
    echo -e "${RED}❌ Requirements dosyaları eksik!${NC}"
    exit 1
fi

# 4. render.yaml kontrolü
if [ -f render.yaml ]; then
    echo -e "${GREEN}✅ render.yaml mevcut${NC}"
else
    echo -e "${RED}❌ render.yaml bulunamadı!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}📦 Dosyalar hazırlanıyor...${NC}"

# Hassas dosyaları temizle
rm -f *.session *.session-journal
rm -f .env
echo -e "${GREEN}✅ Hassas dosyalar temizlendi${NC}"

# Git add
git add .
echo -e "${GREEN}✅ Dosyalar stage'e eklendi${NC}"

# Commit
echo ""
read -p "📝 Commit mesajı girin (varsayılan: 'Deploy to Render'): " commit_msg
commit_msg=${commit_msg:-"Deploy to Render"}

git commit -m "$commit_msg"
echo -e "${GREEN}✅ Commit oluşturuldu${NC}"

# Remote kontrolü
echo ""
if git remote | grep -q origin; then
    echo -e "${GREEN}✅ Git remote mevcut${NC}"
    echo ""
    read -p "🔄 Mevcut remote'a push edilsin mi? (e/h): " push_confirm
    if [ "$push_confirm" = "e" ]; then
        git push origin main
        echo -e "${GREEN}✅ Push tamamlandı!${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Git remote yok${NC}"
    echo ""
    read -p "🔗 GitHub repository URL'i girin: " repo_url
    if [ ! -z "$repo_url" ]; then
        git remote add origin "$repo_url"
        git branch -M main
        git push -u origin main
        echo -e "${GREEN}✅ Push tamamlandı!${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 Deployment hazırlığı tamamlandı!${NC}"
echo ""
echo "📋 Sonraki Adımlar:"
echo "1. https://render.com adresine git"
echo "2. 'New +' → 'Web Service' seç"
echo "3. GitHub repository'ni bağla"
echo "4. Environment variables ekle:"
echo "   - TELEGRAM_API_ID"
echo "   - TELEGRAM_API_HASH"
echo "   - TELEGRAM_PHONE"
echo "5. 'Create Web Service' butonuna tıkla"
echo ""
echo "📖 Detaylı rehber: RENDER_DEPLOYMENT.md"
echo ""
