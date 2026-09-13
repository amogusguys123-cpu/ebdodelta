-- TREINAMENTO FÍSICO - GUI MOBILE
-- Interface nativa, responsiva e compatível com toque.
-- Use como LocalScript em StarterPlayer > StarterPlayerScripts.
--
-- Esta versão não usa loadstring, biblioteca remota ou executor.
-- Ela é um painel manual para uma experiência autorizada.

local Players = game:GetService("Players")
local player = Players.LocalPlayer

local RULES = {
    ["Praças"] = {
        jj = 150, jjTime = 210, pass = 4,
        parkours = {
            A = {35, 40, 30, 32},
            B = {30, 35, 30, 28},
            C = {30, 35, 35, 40},
            D = {35, 30, 30, 40},
        },
    },
    ["Graduados"] = {
        jj = 170, jjTime = 230, pass = 5,
        parkours = {
            A = {30, 35, 27, 29},
            B = {27, 30, 27, 25},
            C = {25, 27, 27, 30},
            D = {27, 25, 25, 30},
        },
    },
}

local role = "Praças"
local version = "A"
local device = "PC/Console"
local participants = {}
local nextId = 0
local currentPage = "Avaliação"

local C = {
    background = Color3.fromRGB(14, 18, 24),
    surface = Color3.fromRGB(24, 30, 40),
    surface2 = Color3.fromRGB(34, 42, 54),
    green = Color3.fromRGB(48, 170, 103),
    greenDark = Color3.fromRGB(31, 106, 68),
    blue = Color3.fromRGB(73, 133, 218),
    orange = Color3.fromRGB(207, 139, 54),
    red = Color3.fromRGB(190, 73, 75),
    white = Color3.fromRGB(242, 246, 248),
    gray = Color3.fromRGB(166, 178, 190),
}

local gui = Instance.new("ScreenGui")
gui.Name = "TreinamentoFisicoMobile"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = false
gui.Parent = player:WaitForChild("PlayerGui")

local main = Instance.new("Frame")
main.Name = "Window"
main.AnchorPoint = Vector2.new(0.5, 0.5)
main.Position = UDim2.fromScale(0.5, 0.5)
main.Size = UDim2.new(1, -16, 1, -16)
main.BackgroundColor3 = C.background
main.BorderSizePixel = 0
main.Parent = gui

local mainCorner = Instance.new("UICorner")
mainCorner.CornerRadius = UDim.new(0, 14)
mainCorner.Parent = main

local function corner(object, radius)
    local c = Instance.new("UICorner")
    c.CornerRadius = UDim.new(0, radius or 8)
    c.Parent = object
end

local function text(parent, value, size, position, color, font)
    local object = Instance.new("TextLabel")
    object.BackgroundTransparency = 1
    object.Text = value
    object.TextColor3 = color or C.white
    object.TextSize = size or 14
    object.Font = font or Enum.Font.Gotham
    object.TextXAlignment = Enum.TextXAlignment.Left
    object.TextYAlignment = Enum.TextYAlignment.Center
    object.Size = UDim2.new(1, 0, 0, 24)
    object.Position = position or UDim2.fromOffset(0, 0)
    object.Parent = parent
    return object
end

local function button(parent, value, size, position, callback, color)
    local object = Instance.new("TextButton")
    object.BackgroundColor3 = color or C.surface2
    object.BorderSizePixel = 0
    object.AutoButtonColor = true
    object.Text = value
    object.TextColor3 = C.white
    object.TextSize = 13
    object.Font = Enum.Font.GothamSemibold
    object.Size = size
    object.Position = position or UDim2.fromOffset(0, 0)
    object.Parent = parent
    corner(object, 8)
    object.Activated:Connect(callback)
    return object
end

local function input(parent, placeholder, size, position)
    local object = Instance.new("TextBox")
    object.BackgroundColor3 = C.surface2
    object.BorderSizePixel = 0
    object.PlaceholderText = placeholder
    object.PlaceholderColor3 = C.gray
    object.Text = ""
    object.TextColor3 = C.white
    object.TextSize = 13
    object.Font = Enum.Font.Gotham
    object.ClearTextOnFocus = false
    object.Size = size
    object.Position = position or UDim2.fromOffset(0, 0)
    object.Parent = parent
    corner(object, 8)
    return object
end

local header = Instance.new("Frame")
header.BackgroundColor3 = C.greenDark
header.BorderSizePixel = 0
header.Size = UDim2.new(1, 0, 0, 58)
header.Parent = main
corner(header, 14)

local headerTitle = text(header, "TREINAMENTO FÍSICO", 17, UDim2.fromOffset(18, 8), C.white, Enum.Font.GothamBold)
headerTitle.Size = UDim2.new(1, -70, 0, 24)
local headerSubtitle = text(header, "Painel mobile do instrutor", 11, UDim2.fromOffset(18, 31), C.gray)
headerSubtitle.Size = UDim2.new(1, -70, 0, 18)

local close = button(header, "×", UDim2.fromOffset(42, 42), UDim2.new(1, -50, 0, 8), function()
    gui.Enabled = false
end, C.red)
close.TextSize = 24

local tabBar = Instance.new("Frame")
tabBar.BackgroundTransparency = 1
tabBar.Size = UDim2.new(1, -20, 0, 46)
tabBar.Position = UDim2.fromOffset(10, 64)
tabBar.Parent = main

local pages = {}
local tabButtons = {}
local tabs = {"Avaliação", "Patente", "Ajuda"}
local refreshSelectors
local renderCards

local function newPage(name)
    local page = Instance.new("ScrollingFrame")
    page.Name = name
    page.BackgroundTransparency = 1
    page.BorderSizePixel = 0
    page.Position = UDim2.fromOffset(10, 116)
    page.Size = UDim2.new(1, -20, 1, -126)
    page.ScrollBarThickness = 5
    page.ScrollBarImageColor3 = C.green
    page.AutomaticCanvasSize = Enum.AutomaticSize.Y
    page.CanvasSize = UDim2.fromOffset(0, 0)
    page.Visible = false
    page.Parent = main
    local layout = Instance.new("UIListLayout")
    layout.Padding = UDim.new(0, 10)
    layout.SortOrder = Enum.SortOrder.LayoutOrder
    layout.Parent = page
    pages[name] = page
    return page
end

for index, name in ipairs(tabs) do
    local tab = button(tabBar, name, UDim2.new(1 / 3, -7, 1, 0), UDim2.new((index - 1) / 3, (index - 1) * 7, 0, 0), function()
        currentPage = name
        for tabName, page in pairs(pages) do
            page.Visible = tabName == currentPage
        end
        for tabName, tabButton in pairs(tabButtons) do
            tabButton.BackgroundColor3 = tabName == currentPage and C.green or C.surface
        end
    end, name == currentPage and C.green or C.surface)
    tabButtons[name] = tab
end

local evaluationPage = newPage("Avaliação")
local rankPage = newPage("Patente")
local helpPage = newPage("Ajuda")

local selectorCard = Instance.new("Frame")
selectorCard.BackgroundColor3 = C.surface
selectorCard.Size = UDim2.new(1, 0, 0, 160)
selectorCard.Parent = evaluationPage
corner(selectorCard)

local selectorTitle = text(selectorCard, "CONFIGURAÇÃO", 13, UDim2.fromOffset(14, 10), C.gray, Enum.Font.GothamBold)
selectorTitle.Size = UDim2.new(1, -28, 0, 20)

local roleButton = button(selectorCard, "", UDim2.new(0.5, -19, 0, 38), UDim2.fromOffset(14, 38), function()
    role = role == "Praças" and "Graduados" or "Praças"
    refreshSelectors()
    renderCards()
end, C.green)

local versionButton = button(selectorCard, "", UDim2.new(0.5, -19, 0, 38), UDim2.new(0.5, 5, 0, 38), function()
    local order = {"A", "B", "C", "D"}
    local index = table.find(order, version) or 1
    version = order[index % #order + 1]
    refreshSelectors()
    renderCards()
end)

local deviceButton = button(selectorCard, "", UDim2.new(0.5, -19, 0, 38), UDim2.fromOffset(14, 82), function()
    device = device == "PC/Console" and "Celular" or "PC/Console"
    refreshSelectors()
end)

local rulesLabel = text(selectorCard, "", UDim2.new(0.5, -19, 0, 38), UDim2.new(0.5, 5, 0, 82), C.gray, Enum.Font.Gotham)
rulesLabel.TextWrapped = true
rulesLabel.TextSize = 10

refreshSelectors = function()
    local rules = RULES[role]
    roleButton.Text = role
    versionButton.Text = "Parkour " .. version
    deviceButton.Text = "Torre: " .. device
    rulesLabel.Text = string.format("%d JJs / %ds\nAprovação: %d pontos", rules.jj, rules.jjTime, rules.pass)
end

local addCard = Instance.new("Frame")
addCard.BackgroundColor3 = C.surface
addCard.Size = UDim2.new(1, 0, 0, 74)
addCard.Parent = evaluationPage
corner(addCard)

local nameInput = input(addCard, "Nome do participante", UDim2.new(1, -116, 0, 42), UDim2.fromOffset(10, 16))
local addButton = button(addCard, "+", UDim2.fromOffset(82, 42), UDim2.new(1, -92, 0, 16), function()
    local name = nameInput.Text:gsub("^%s+", ""):gsub("%s+$", "")
    if name ~= "" then
        nextId += 1
        table.insert(participants, {
            id = nextId,
            name = name,
            score = 0,
            awards = {JJ = 0, P1 = 0, P2 = 0, P3 = 0, P4 = 0, TEXT = 0, QUESTION = 0},
            timers = {},
            jjCount = "",
            textErrors = "",
            theme = true,
        })
        nameInput.Text = ""
    end
end, C.green)
addButton.TextSize = 24

local cards = Instance.new("Frame")
cards.Name = "ParticipantCards"
cards.BackgroundTransparency = 1
cards.Size = UDim2.new(1, 0, 0, 0)
cards.AutomaticSize = Enum.AutomaticSize.Y
cards.Parent = evaluationPage
local cardsLayout = Instance.new("UIListLayout")
cardsLayout.Padding = UDim.new(0, 10)
cardsLayout.SortOrder = Enum.SortOrder.LayoutOrder
cardsLayout.Parent = cards

local function award(participant, key, value)
    participant.score -= participant.awards[key] or 0
    participant.awards[key] = math.max(0, value)
    participant.score += participant.awards[key]
end

local function timerButtonText(participant, key, prefix)
    local timer = participant.timers[key]
    if not timer then
        return prefix .. " iniciar"
    end
    if not timer.elapsed then
        return prefix .. " parar"
    end
    return prefix .. " " .. timer.elapsed .. "s"
end

local function toggleTimer(participant, key, limit)
    local timer = participant.timers[key]
    if not timer then
        participant.timers[key] = {started = os.clock()}
    elseif not timer.elapsed then
        timer.elapsed = math.floor(os.clock() - timer.started + 0.5)
        local passed = timer.elapsed <= limit
        award(participant, key, passed and 1 or 0)
    end
    renderCards()
end

local function calculateText(participant)
    local errors = tonumber(participant.textErrors) or 99
    local points = 0
    if participant.theme and errors == 0 then
        points = 2
    elseif participant.theme and errors <= 3 then
        points = 1
    end
    award(participant, "TEXT", points)
    renderCards()
end

renderCards = function()
    for _, child in ipairs(cards:GetChildren()) do
        if child:IsA("Frame") then
            child:Destroy()
        end
    end

    local rules = RULES[role]
    local limits = rules.parkours[version]

    for order, participant in ipairs(participants) do
        local card = Instance.new("Frame")
        card.BackgroundColor3 = C.surface
        card.Size = UDim2.new(1, 0, 0, 280)
        card.LayoutOrder = order
        card.Parent = cards
        corner(card)

        local nameLabel = text(card, participant.name, UDim2.new(0.65, 0, 0, 25), UDim2.fromOffset(14, 10), C.white, Enum.Font.GothamBold)
        local approved = participant.score >= rules.pass
        local scoreLabel = text(card, string.format("%d/9 • %s", participant.score, approved and "APROVADO" or "EM AVALIAÇÃO"), UDim2.new(0.35, -14, 0, 25), UDim2.new(0.65, 0, 0, 10), approved and C.green or C.gray, Enum.Font.GothamSemibold)
        scoreLabel.TextXAlignment = Enum.TextXAlignment.Right

        local jjInput = input(card, "JJs feitos", UDim2.new(0.5, -20, 0, 34), UDim2.fromOffset(14, 43))
        jjInput.Text = participant.jjCount
        jjInput.FocusLost:Connect(function()
            participant.jjCount = jjInput.Text
        end)

        local delete = button(card, "Remover", UDim2.new(0.5, -20, 0, 34), UDim2.new(0.5, 6, 0, 43), function()
            for i, item in ipairs(participants) do
                if item.id == participant.id then
                    table.remove(participants, i)
                    break
                end
            end
            renderCards()
        end, C.red)

        local actions = Instance.new("Frame")
        actions.BackgroundTransparency = 1
        actions.Size = UDim2.new(1, -28, 0, 138)
        actions.Position = UDim2.fromOffset(14, 88)
        actions.Parent = card
        local grid = Instance.new("UIGridLayout")
        grid.CellPadding = UDim2.fromOffset(8, 8)
        grid.CellSize = UDim2.new(0.5, -4, 0, 38)
        grid.SortOrder = Enum.SortOrder.LayoutOrder
        grid.Parent = actions

        local jj = button(actions, timerButtonText(participant, "JJ", "JJ"), UDim2.fromOffset(1, 1), nil, function()
            local count = tonumber(participant.jjCount) or 0
            local timer = participant.timers.JJ
            if not timer then
                participant.timers.JJ = {started = os.clock()}
                renderCards()
            elseif not timer.elapsed then
                timer.elapsed = math.floor(os.clock() - timer.started + 0.5)
                local passed = timer.elapsed <= rules.jjTime and count >= rules.jj
                award(participant, "JJ", passed and 1 or 0)
                renderCards()
            end
        end, C.green)
        jj.LayoutOrder = 1

        for p = 1, 4 do
            local key = "P" .. p
            local parkour = button(actions, timerButtonText(participant, key, "P" .. p), UDim2.fromOffset(1, 1), nil, function()
                toggleTimer(participant, key, limits[p])
            end)
            parkour.LayoutOrder = p + 1
        end

        local textInput = input(card, "Erros no texto", UDim2.new(0.5, -20, 0, 34), UDim2.fromOffset(14, 238))
        textInput.Text = participant.textErrors
        textInput.FocusLost:Connect(function()
            participant.textErrors = textInput.Text
        end)

        local textButton = button(card, "Texto: " .. participant.awards.TEXT .. "p", UDim2.new(0.5, -20, 0, 34), UDim2.new(0.5, 6, 0, 238), function()
            calculateText(participant)
        end, C.orange)
        textButton.LayoutOrder = 10
    end
end

local rankCard = Instance.new("Frame")
rankCard.BackgroundColor3 = C.surface
rankCard.Size = UDim2.new(1, 0, 0, 260)
rankCard.Parent = rankPage
corner(rankCard)

local rankTitle = text(rankCard, "ENTREGA DE PONTOS", 15, UDim2.fromOffset(14, 14), C.white, Enum.Font.GothamBold)
rankTitle.Size = UDim2.new(1, -28, 0, 25)
local rankInfo = text(rankCard, "Prepare o comando, confira o Nick e copie manualmente.", 11, UDim2.fromOffset(14, 40), C.gray)
rankInfo.Size = UDim2.new(1, -28, 0, 22)

local rankNick = input(rankCard, "Nick exato", UDim2.new(0.58, -19, 0, 42), UDim2.fromOffset(14, 76))
local rankAmount = input(rankCard, "Pontos", UDim2.new(0.42, -19, 0, 42), UDim2.new(0.58, 5, 0, 76))
local rankCommand = input(rankCard, "Comando aparecerá aqui", UDim2.new(1, -28, 0, 42), UDim2.fromOffset(14, 128))
rankCommand.ClearTextOnFocus = false

local prepare = button(rankCard, "Preparar comando", UDim2.new(0.5, -19, 0, 42), UDim2.fromOffset(14, 182), function()
    local nick = rankNick.Text:gsub("^%s+", ""):gsub("%s+$", "")
    local amount = rankAmount.Text:gsub("%D", "")
    if nick == "" or amount == "" then
        rankCommand.Text = "Preencha Nick e pontos."
    else
        rankCommand.Text = ";titler " .. nick .. " " .. amount
    end
end, C.green)

local selectCommand = button(rankCard, "Selecionar / copiar", UDim2.new(0.5, -19, 0, 42), UDim2.new(0.5, 5, 0, 182), function()
    if rankCommand.Text ~= "" then
        rankCommand:CaptureFocus()
        rankCommand.SelectionStart = 1
        rankCommand.CursorPosition = #rankCommand.Text + 1
    end
end)

local helpCard = Instance.new("Frame")
helpCard.BackgroundColor3 = C.surface
helpCard.Size = UDim2.new(1, 0, 0, 430)
helpCard.Parent = helpPage
corner(helpCard)

local helpText = text(helpCard, [[COMO USAR

1. Em Avaliação, escolha Praças ou Graduados.
2. Escolha a versão do parkour e o dispositivo da torre.
3. Adicione cada participante pelo nome.
4. Informe a quantidade de JJs e use os botões para iniciar/parar os cronômetros.
5. Digite os erros do texto e toque em Texto para calcular.
6. A entrega de pontos fica na aba Patente.

CRITÉRIOS

Praças: 150 JJs em 210 segundos. Mínimo: 4 pontos.
Graduados: 170 JJs em 230 segundos. Mínimo: 5 pontos.
Texto: 0 erros = 2 pontos; 1 a 3 = 1 ponto; mais de 3 = 0.
Cada parkour vale 1 ponto. Perguntas devem ser conferidas manualmente.

O painel não lê dados ocultos, não executa comandos ao tocar
em jogadores e não substitui a validação do servidor.]], 13, UDim2.fromOffset(16, 14), C.white)
helpText.Size = UDim2.new(1, -32, 1, -28)
helpText.TextWrapped = true
helpText.TextYAlignment = Enum.TextYAlignment.Top

refreshSelectors()
renderCards()
pages["Avaliação"].Visible = true
