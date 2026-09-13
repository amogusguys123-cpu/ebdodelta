--[[
    EXÉRCITO BRASILEIRO DO DELTA
    TREINAMENTO FÍSICO • WINDUI OFICIAL

    Uso: LocalScript em StarterPlayer > StarterPlayerScripts.
    Requer o módulo WindUI oficial em:
    ReplicatedStorage > WindUI > Init

    Este painel é apenas um apoio manual para avaliação dentro da experiência.
    Não executa comandos administrativos, não burla o jogo e não altera o servidor.
]]

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer

-- =========================================================
-- WINDUI REMOTO (CARREGAMENTO UNIVERSAL)
-- =========================================================
local WindUI
local success, result = pcall(function()
    return loadstring(game:HttpGet("raw.githubusercontent.com/Footagesus/WindUI/main/main.lua"))()
end)

if success and result then
    WindUI = result
else
    error("Não foi possível carregar o WindUI remotamente. Verifique seu executador.")
end


-- =========================================================
-- REGRAS DO DOCUMENTO OFICIAL DO EB DELTA
-- =========================================================
local RULES = {
    ["Praças"] = {
        jj = 150,
        jjTime = 210,
        pass = 4,
        parkours = {
            A = {35, 40, 30, 32},
            B = {30, 35, 30, 28},
            C = {30, 35, 35, 40},
            D = {35, 30, 30, 40},
        },
    },

    ["Graduados"] = {
        jj = 170,
        jjTime = 230,
        pass = 5,
        parkours = {
            A = {30, 35, 27, 29},
            B = {27, 30, 27, 25},
            C = {25, 27, 27, 30},
            D = {27, 25, 25, 30},
        },
    },
}

local TEXT_TIME = 400
local QUESTION_TIME = 40
local TOWER_LIMITS = {
    ["PC/Console"] = 15,
    ["Celular"] = 16,
}

local role = "Praças"
local version = "A"
local device = "PC/Console"

local participants = {}
local nextId = 0

-- =========================================================
-- UTILITÁRIOS
-- =========================================================
local function trim(value)
    return tostring(value or ""):gsub("^%s+", ""):gsub("%s+$", "")
end

local function notify(title, content)
    WindUI:Notify({
        Title = title,
        Content = content,
    })
end

local function getRules()
    return RULES[role]
end

local function calculateScore(p)
    local total = 0
    for _, value in pairs(p.awards) do
        total += tonumber(value) or 0
    end
    return total
end

local function statusText(p)
    local score = calculateScore(p)
    if score >= getRules().pass then
        return "APROVADO"
    end
    return "EM AVALIAÇÃO"
end

local function timerText(p, key, label)
    local timer = p.timers[key]

    if not timer then
        return label .. " • iniciar"
    end

    if not timer.elapsed then
        local live = math.floor(os.clock() - timer.started)
        return string.format("%s • %ds...", label, live)
    end

    return string.format("%s • %ds", label, timer.elapsed)
end

-- =========================================================
-- JANELA WINDUI
-- =========================================================
local Window = WindUI:CreateWindow({
    Title = "Exército Brasileiro do Delta",
    Icon = "shield-check",
    Folder = "EBDelta_TreinamentoFisico",
    NewElements = true,
    HideSearchBar = false,

    OpenButton = {
        Title = "Abrir Treinamento",
        Enabled = true,
        Draggable = true,
        OnlyMobile = false,
        Scale = 0.8,
    },

    Topbar = {
        Height = 44,
        ButtonsType = "Mac",
    },
})

Window:Tag({
    Title = "EB DELTA",
    Icon = "shield-check",
    Border = true,
})

Window:Tag({
    Title = "TREINAMENTO FÍSICO",
    Icon = "clipboard-check",
    Border = true,
})

-- =========================================================
-- SEÇÕES / ABAS
-- =========================================================
local EvaluationTab = Window:Tab({
    Title = "Avaliação",
    Icon = "clipboard-check",
    Border = true,
})

local CommandsTab = Window:Tab({
    Title = "Comandos",
    Icon = "terminal",
    Border = true,
})

local RulesTab = Window:Tab({
    Title = "Regras",
    Icon = "book-open",
    Border = true,
})

local AboutTab = Window:Tab({
    Title = "Sobre",
    Icon = "info",
    Border = true,
})

-- =========================================================
-- AVALIAÇÃO
-- =========================================================
local ConfigSection = EvaluationTab:Section({
    Title = "Configuração do treinamento",
    Box = true,
    Opened = true,
})

local roleDropdown = ConfigSection:Dropdown({
    Title = "Marcação",
    Values = {"Praças", "Graduados"},
    Value = role,
    AllowNone = false,
    Callback = function(value)
        role = value
        refreshParticipantCards()
    end,
})

local versionDropdown = ConfigSection:Dropdown({
    Title = "Versão do Parkour",
    Values = {"A", "B", "C", "D"},
    Value = version,
    AllowNone = false,
    Callback = function(value)
        version = value
        refreshParticipantCards()
    end,
})

local deviceDropdown = ConfigSection:Dropdown({
    Title = "Dispositivo da Torre",
    Values = {"PC/Console", "Celular"},
    Value = device,
    AllowNone = false,
    Callback = function(value)
        device = value
        refreshParticipantCards()
    end,
})

local RulesSection = EvaluationTab:Section({
    Title = "Resumo da avaliação",
    Box = true,
    Opened = true,
})

local rulesParagraph = RulesSection:Paragraph({
    Title = "Regras atuais",
    Desc = "",
})

local AddSection = EvaluationTab:Section({
    Title = "Participantes",
    Box = true,
    Opened = true,
})

local participantInput = AddSection:Input({
    Title = "Adicionar participante",
    Placeholder = "Digite o Nick exato",
    Callback = function(value)
        participantInputValue = value
    end,
})

local addParticipantButton = AddSection:Button({
    Title = "Adicionar",
    Icon = "user-plus",
    Callback = function()
        local name = trim(participantInputValue)

        if name == "" then
            notify("EB Delta", "Digite o Nick do participante.")
            return
        end

        nextId += 1

        table.insert(participants, {
            id = nextId,
            name = name,

            awards = {
                JJ = 0,
                P1 = 0,
                P2 = 0,
                P3 = 0,
                P4 = 0,
                TEXT = 0,
                QUESTION = 0,
            },

            timers = {},

            jjCount = "",
            textErrors = "",
            textTheme = true,
            questionCorrect = false,
        })

        participantInputValue = ""
        notify("Participante", name .. " foi adicionado.")
        refreshParticipantCards()
    end,
})

local ParticipantsSection = EvaluationTab:Section({
    Title = "Avaliações individuais",
    Box = true,
    Opened = true,
})

local participantElements = {}

-- =========================================================
-- DECLARAÇÕES ANTECIPADAS
-- =========================================================
refreshParticipantCards = function() end

local function refreshRules()
    local r = getRules()
    local p = r.parkours[version]

    rulesParagraph:SetDesc(string.format(
        "Marcação: %s\nJJ: %d em %ds\nParkour %s: P1 %ds • P2 %ds • P3 %ds • P4 %ds\nTorre: %ds (%s)\nTexto: %ds\nPergunta: %ds\nAprovação: %d pontos",
        role,
        r.jj,
        r.jjTime,
        version,
        p[1], p[2], p[3], p[4],
        TOWER_LIMITS[device],
        device,
        TEXT_TIME,
        QUESTION_TIME,
        r.pass
    ))
end

local function removeParticipant(id)
    for index, p in ipairs(participants) do
        if p.id == id then
            table.remove(participants, index)
            break
        end
    end

    refreshParticipantCards()
end

local function setAward(p, key, value)
    p.awards[key] = math.max(0, tonumber(value) or 0)
end

local function finishTimer(p, key, limit, awardKey)
    local timer = p.timers[key]

    if not timer then
        p.timers[key] = {
            started = os.clock(),
        }
        refreshParticipantCards()
        return
    end

    if timer.elapsed then
        return
    end

    timer.elapsed = math.floor(os.clock() - timer.started + 0.5)
    setAward(p, awardKey or key, timer.elapsed <= limit and 1 or 0)

    refreshParticipantCards()
end

local function calculateText(p)
    local errors = tonumber(p.textErrors)

    if not errors then
        setAward(p, "TEXT", 0)
        notify("Texto", "Informe a quantidade de erros.")
        return
    end

    if not p.textTheme then
        setAward(p, "TEXT", 0)
    elseif errors == 0 then
        setAward(p, "TEXT", 2)
    elseif errors <= 3 then
        setAward(p, "TEXT", 1)
    else
        setAward(p, "TEXT", 0)
    end

    refreshParticipantCards()
end

local function setQuestion(p, correct)
    p.questionCorrect = correct
    setAward(p, "QUESTION", correct and 1 or 0)
    refreshParticipantCards()
end

refreshParticipantCards = function()
    refreshRules()

    for _, element in ipairs(participantElements) do
        pcall(function()
            element:Destroy()
        end)
    end

    table.clear(participantElements)

    local r = getRules()
    local limits = r.parkours[version]

    if #participants == 0 then
        local empty = ParticipantsSection:Paragraph({
            Title = "Nenhum participante",
            Desc = "Adicione um Nick acima para começar a avaliação.",
        })

        table.insert(participantElements, empty)
        return
    end

    for _, p in ipairs(participants) do
        local score = calculateScore(p)
        local approved = score >= r.pass

        local section = ParticipantsSection:Section({
            Title = p.name .. " • " .. score .. "/9 • " .. statusText(p),
            Box = true,
            Opened = true,
        })

        table.insert(participantElements, section)

        section:Paragraph({
            Title = "Resumo",
            Desc = string.format(
                "Aprovação: %d pontos | Pontuação atual: %d/9\nJJ: %d | P1: %d | P2: %d | P3: %d | P4: %d | Texto: %d | Pergunta: %d",
                r.pass,
                score,
                p.awards.JJ,
                p.awards.P1,
                p.awards.P2,
                p.awards.P3,
                p.awards.P4,
                p.awards.TEXT,
                p.awards.QUESTION
            ),
        })

        section:Input({
            Title = "Quantidade de JJs",
            Placeholder = "Ex.: " .. r.jj,
            Value = p.jjCount,
            Callback = function(value)
                p.jjCount = value
            end,
        })

        section:Button({
            Title = timerText(p, "JJ", "JJ"),
            Icon = "timer",
            Callback = function()
                local count = tonumber(p.jjCount) or 0
                local timer = p.timers.JJ

                if not timer then
                    p.timers.JJ = {
                        started = os.clock(),
                    }
                    refreshParticipantCards()
                    return
                end

                if timer.elapsed then
                    return
                end

                timer.elapsed = math.floor(os.clock() - timer.started + 0.5)

                local passed = count >= r.jj and timer.elapsed <= r.jjTime
                setAward(p, "JJ", passed and 1 or 0)

                refreshParticipantCards()
            end,
        })

        section:Button({
            Title = timerText(p, "P1", "Parkour 1"),
            Icon = "timer",
            Callback = function()
                finishTimer(p, "P1", limits[1], "P1")
            end,
        })

        section:Button({
            Title = timerText(p, "P2", "Parkour 2"),
            Icon = "timer",
            Callback = function()
                finishTimer(p, "P2", limits[2], "P2")
            end,
        })

        section:Button({
            Title = timerText(p, "P3", "Parkour 3"),
            Icon = "timer",
            Callback = function()
                finishTimer(p, "P3", limits[3], "P3")
            end,
        })

        section:Button({
            Title = timerText(p, "P4", "Parkour 4"),
            Icon = "timer",
            Callback = function()
                finishTimer(p, "P4", limits[4], "P4")
            end,
        })

        section:Input({
            Title = "Erros gramaticais",
            Placeholder = "0, 1, 2, 3...",
            Value = p.textErrors,
            Callback = function(value)
                p.textErrors = value
            end,
        })

        section:Toggle({
            Title = "Texto dentro do tema",
            Value = p.textTheme,
            Callback = function(value)
                p.textTheme = value
                calculateText(p)
            end,
        })

        section:Button({
            Title = "Calcular texto",
            Icon = "file-check",
            Callback = function()
                calculateText(p)
            end,
        })

        section:Toggle({
            Title = "Pergunta respondida corretamente",
            Value = p.questionCorrect,
            Callback = function(value)
                setQuestion(p, value)
            end,
        })

        section:Button({
            Title = "Torre • " .. device .. " • limite " .. TOWER_LIMITS[device] .. "s",
            Icon = "timer",
            Callback = function()
                finishTimer(p, "TOWER", TOWER_LIMITS[device], "TOWER")
            end,
        })

        section:Button({
            Title = "Remover participante",
            Icon = "trash-2",
            Callback = function()
                removeParticipant(p.id)
            end,
        })
    end
end

-- =========================================================
-- COMANDOS
-- =========================================================
local CommandSection = CommandsTab:Section({
    Title = "Preparação de comandos",
    Box = true,
    Opened = true,
})

CommandSection:Paragraph({
    Title = "Uso manual",
    Desc = "Os comandos abaixo são apenas textos de referência. O painel não executa comandos administrativos.",
})

local commandNick = ""
local commandText = ""

CommandSection:Input({
    Title = "Nick",
    Placeholder = "Nick exato",
    Callback = function(value)
        commandNick = trim(value)
    end,
})

CommandSection:Button({
    Title = "Preparar ;titler",
    Icon = "badge",
    Callback = function()
        if commandNick == "" then
            notify("Comando", "Informe o Nick.")
            return
        end

        commandText = ";titler " .. commandNick
        notify("Comando preparado", commandText)
    end,
})

CommandSection:Paragraph({
    Title = "Comandos do documento",
    Desc = ";countdown (Tempo)\n;h (Mensagem)\n;title (Nick)\n;kick (Nick)\n\nUse-os somente conforme as permissões e regras da experiência.",
})

-- =========================================================
-- REGRAS
-- =========================================================
local OfficialSection = RulesTab:Section({
    Title = "Regras oficiais do Treinamento Físico",
    Box = true,
    Opened = true,
})

OfficialSection:Paragraph({
    Title = "Antes do treinamento",
    Desc = "Não poste o anúncio sem estar dentro do servidor. Organize os participantes, aguarde a tolerância informada e siga as orientações do instrutor.",
})

OfficialSection:Paragraph({
    Title = "JJ's",
    Desc = "Praças: 150 em 210s.\nGraduados: 170 em 230s.\nVale 1 ponto.",
})

OfficialSection:Paragraph({
    Title = "Texto gramatical",
    Desc = "400 segundos. Mínimo de 3 linhas. Tema: Exército Brasileiro ou Exército Brasileiro do Delta.\n0 erros = 2 pontos.\n1 a 3 erros = 1 ponto.\nMais de 3 erros ou fuga do tema = 0.",
})

OfficialSection:Paragraph({
    Title = "Parkours",
    Desc = "Cada parkour vale 1 ponto.\n\nPraças:\nA 35/40/30/32\nB 30/35/30/28\nC 30/35/35/40\nD 35/30/30/40\n\nGraduados:\nA 30/35/27/29\nB 27/30/27/25\nC 25/27/27/30\nD 27/25/25/30.",
})

OfficialSection:Paragraph({
    Title = "Torre",
    Desc = "PC/Console: 15 segundos.\nCelular: 16 segundos.",
})

OfficialSection:Paragraph({
    Title = "Perguntas",
    Desc = "1 pergunta relacionada ao EB do Delta ou ao Exército Brasileiro.\nTimer de 40 segundos.\nSó recebe ponto quem acertar.",
})

OfficialSection:Paragraph({
    Title = "Aprovação",
    Desc = "Praças: mínimo 4 pontos.\nGraduados: mínimo 5 pontos.\nMáximo informado no documento: 9 pontos.",
})

OfficialSection:Paragraph({
    Title = "Conduta",
    Desc = "Sem favoritismo. Siga as mesmas condições para todos os avaliados. O documento também proíbe meio ponto, pontos extras por desempenho e outras alterações das regras.",
})

-- =========================================================
-- SOBRE
-- =========================================================
local AboutSection = AboutTab:Section({
    Title = "Exército Brasileiro do Delta",
    Box = true,
    Opened = true,
})

AboutSection:Paragraph({
    Title = "Treinamento Físico",
    Desc = "Painel de apoio ao instrutor para organização manual das avaliações de Praças e Graduados.",
})

AboutSection:Paragraph({
    Title = "WindUI",
    Desc = "Interface construída usando a API oficial do projeto WindUI, sem fork/modificação da biblioteca.",
})

AboutSection:Paragraph({
    Title = "Importante",
    Desc = "Este painel não substitui a validação do servidor, não lê dados ocultos e não executa comandos administrativos automaticamente.",
})

-- =========================================================
-- INICIALIZAÇÃO
-- =========================================================
refreshParticipantCards()

notify(
    "EB Delta",
    "Painel de Treinamento Físico carregado."
)
