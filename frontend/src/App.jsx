import React, { useState, useEffect } from 'react';
import { MessageSquare, Search, Map, BarChart2, Calendar, User, Home, BookOpen, Activity, Layers, Settings, Bell, MapPin, ArrowRight, Zap, Download, Share2, Heart, Briefcase, Bus } from 'lucide-react';

const App = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: 'Olá! Sou a Ana, assistente virtual do Recife. Como posso ajudar você a encontrar informações sobre a cidade?'
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('discover');
  const [viewportWidth, setViewportWidth] = useState(window.innerWidth);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [agentType, setAgentType] = useState('GERAL');
  const [conversationId, setConversationId] = useState(`conv_${Date.now()}`);
  const [showHowItWorks, setShowHowItWorks] = useState(false);

  const formatMarkdown = (text) => {
    if (!text) return null;

    const paragraphs = text.split('\n\n');

    return paragraphs.map((paragraph, idx) => {
      if (paragraph.startsWith('# ')) {
        return <h1 key={idx} className="text-lg font-bold my-2">{paragraph.substring(2)}</h1>;
      }
      if (paragraph.startsWith('## ')) {
        return <h2 key={idx} className="text-md font-bold my-2">{paragraph.substring(3)}</h2>;
      }

      if (paragraph.startsWith('### ')) {
        return <h3 key={idx} className="text-md font-bold my-2">{paragraph.substring(4)}</h3>;
      }

      if (paragraph.includes('\n- ')) {
        const listItems = paragraph.split('\n- ');
        return (
          <ul key={idx} className="list-disc pl-4 my-2">
            {listItems.filter(item => item.trim()).map((item, i) => (
              <li key={i} className="mb-1">{item}</li>
            ))}
          </ul>
        );
      }

      if (/\n\d+\./.test(paragraph)) {
        const listItems = paragraph.split(/\n\d+\.\s/);
        return (
          <ol key={idx} className="list-decimal pl-4 my-2">
            {listItems.filter(item => item.trim()).map((item, i) => (
              <li key={i} className="mb-1">{item}</li>
            ))}
          </ol>
        );
      }

      let formattedText = paragraph;
      formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      formattedText = formattedText.replace(/\*(.*?)\*/g, '<em>$1</em>');

      return <p key={idx} className="mb-2" dangerouslySetInnerHTML={{ __html: formattedText }} />;
    });
  };

  useEffect(() => {
    const handleResize = () => {
      setViewportWidth(window.innerWidth);
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      } else {
        setSidebarOpen(true);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { type: 'user', content: query }]);
    setLoading(true);

    try {
      // Prepare the API request
      const requestBody = {
        message: query,
        conversation_id: conversationId,
        tipo_agente: agentType
      };

      // Make the API call to the /message endpoint
      const response = await fetch(`${process.env.BACKEND_API_URL}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      // Create assistant response without visualization type
      const assistantResponse = {
        type: 'assistant',
        content: data.answer
      };

      setMessages(prev => [...prev, assistantResponse]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: 'Desculpe, estou tendo dificuldades para processar sua solicitação no momento. Por favor, tente novamente mais tarde.'
      }]);
    } finally {
      setLoading(false);
      setQuery('');
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 overflow-hidden">
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200 flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
              <Layers size={18} className="text-blue-600" />
            </div>
            <div>
              <h1 className="font-semibold text-lg text-blue-800">Dados Recife</h1>
              <p className="text-xs text-gray-500">Hub de Dados - HackerCidadão 12.0</p>
            </div>
          </div>

          <nav className="flex-1 p-4">
            <ul className="space-y-1">
              <li>
                <a
                  href="#"
                  className={`flex items-center space-x-3 p-2 rounded-lg ${activeTab === 'discover' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                  onClick={() => setActiveTab('discover')}
                >
                  <Search size={18} />
                  <span>Descobrir</span>
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className={`flex items-center space-x-3 p-2 rounded-lg ${activeTab === 'dashboard' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                  onClick={() => setActiveTab('dashboard')}
                >
                  <BarChart2 size={18} />
                  <span>Dashboard</span>
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className={`flex items-center space-x-3 p-2 rounded-lg ${activeTab === 'map' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                  onClick={() => setActiveTab('map')}
                >
                  <Map size={18} />
                  <span>Mapa da Cidade</span>
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className={`flex items-center space-x-3 p-2 rounded-lg ${activeTab === 'events' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-100'}`}
                  onClick={() => setActiveTab('events')}
                >
                  <Calendar size={18} />
                  <span>Eventos</span>
                </a>
              </li>
            </ul>

            <div className="mt-8">
              <h3 className="text-xs uppercase text-gray-500 font-semibold mb-2 pl-2">Meus Interesses</h3>
              <div className="flex flex-wrap gap-2">
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Saúde</span>
                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">Mobilidade</span>
                <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">Educação</span>
                <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">Cultura</span>
                <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">Segurança</span>
                <span className="text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-full">+ Adicionar</span>
              </div>
            </div>
          </nav>

          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                <User size={18} className="text-blue-600" />
              </div>
              <div>
                <p className="text-sm font-medium">Maria Silva</p>
                <p className="text-xs text-gray-500">Boa Viagem</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4">
          {!sidebarOpen && (
            <div className="flex items-center space-x-2">
              <button
                className="p-2 rounded-lg hover:bg-gray-100"
                onClick={() => setSidebarOpen(true)}
              >
                <Layers size={20} className="text-blue-600" />
              </button>
              <h1 className="font-semibold text-lg text-blue-800">Dados Recife</h1>
            </div>
          )}

          <div className="flex-1 max-w-2xl mx-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Pesquisar dados, serviços, eventos..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <Search size={18} className="absolute left-3 top-2.5 text-gray-400" />
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <button className="relative p-2 rounded-lg hover:bg-gray-100">
              <Bell size={20} className="text-gray-600" />
              <span className="absolute top-1 right-1 h-2 w-2 bg-red-500 rounded-full"></span>
            </button>
            <button className="p-2 rounded-lg hover:bg-gray-100">
              <Settings size={20} className="text-gray-600" />
            </button>
          </div>
        </header>

        {/* Main area */}
        <main className="flex-1 overflow-auto p-4">
          <div className="max-w-6xl mx-auto">
            {/* Featured content */}
            <div className="mb-6">
              <div className="bg-gradient-to-r from-blue-100 to-purple-100 rounded-xl p-6 relative overflow-hidden">
                <div className="max-w-lg relative z-10">
                  <h2 className="text-2xl font-bold text-blue-900 mb-2">Seja bem-vindo(a) à VihAI</h2>
                  <p className="text-blue-800 mb-4">
                    Experimente nossa interface com Inteligência Artificial Generativa para desmitificar os dados sobre a cidade de Recife,
                    fazer perguntas em linguagem natural e ter suas respostas e informações de uma maneira simples e concisa.
                  </p>
                  <div className="flex space-x-3">
                    <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2">
                      <MessageSquare size={16} />
                      <span>Fazer uma pergunta</span>
                    </button>
                    <button 
                      onClick={() => setShowHowItWorks(true)}
                      className="bg-white hover:bg-gray-50 text-blue-700 px-4 py-2 rounded-lg border border-blue-200">
                      Como Funciona
                    </button>
                  </div>
                </div>

                {/* Decorative elements - simplified to just the icon */}
                <div className="absolute right-8 bottom-0 top-0 w-64 flex items-center justify-center">
                  <div className="h-12 w-12 bg-white rounded-full shadow-lg flex items-center justify-center">
                    <Zap size={24} className="text-blue-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* AI Conversation Section - Moved above the categories */}
            <div className="mb-8">
              <div className="bg-white rounded-xl shadow-md overflow-hidden">
                <div className="p-4 bg-blue-50 border-b border-blue-100">
                  <h2 className="text-lg font-bold text-blue-800 flex items-center">
                    <MessageSquare size={20} className="mr-2" />
                    Assistente Ana - IA de Dados Recife
                  </h2>
                  <p className="text-sm text-blue-600">
                    Faça perguntas sobre a cidade e obtenha informações em tempo real
                  </p>
                </div>

                <div className="p-4 h-96 overflow-y-auto flex flex-col space-y-4">
                  {messages.map((message, idx) => (
                    <div
                      key={idx}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-3/4 rounded-lg p-3 ${message.type === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-800'
                          }`}
                      >
                        {message.type === 'assistant' ? (
                          <div>{formatMarkdown(message.content)}</div>
                        ) : (
                          <p>{message.content}</p>
                        )}
                      </div>
                    </div>
                  ))}

                  {loading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 rounded-lg p-3 max-w-3/4">
                        <div className="flex space-x-2 items-center">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="p-4 border-t border-gray-200">
                  <div className="mb-3">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Selecione o agente especialista:</label>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => setAgentType('GERAL')}
                        className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${agentType === 'GERAL'
                          ? 'bg-blue-100 text-blue-700 border border-blue-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'}`}
                      >
                        <Layers size={16} />
                        Geral
                      </button>
                      <button
                        onClick={() => setAgentType('CULTURA')}
                        className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${agentType === 'CULTURA'
                          ? 'bg-purple-100 text-purple-700 border border-purple-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'}`}
                      >
                        <Calendar size={16} />
                        Cultura
                      </button>
                      <button
                        onClick={() => setAgentType('SAUDE')}
                        className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${agentType === 'SAUDE'
                          ? 'bg-green-100 text-green-700 border border-green-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'}`}
                      >
                        <Heart size={16} />
                        Saúde
                      </button>
                      <button
                        onClick={() => setAgentType('MOBILIDADE')}
                        className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${agentType === 'MOBILIDADE'
                          ? 'bg-blue-100 text-blue-700 border border-blue-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'}`}
                      >
                        <Bus size={16} />
                        Mobilidade
                      </button>
                      <button
                        onClick={() => setAgentType('SERVICOS')}
                        className={`flex items-center gap-1 px-3 py-1 rounded-lg text-sm ${agentType === 'SERVICOS'
                          ? 'bg-yellow-100 text-yellow-700 border border-yellow-300'
                          : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'}`}
                      >
                        <Briefcase size={16} />
                        Serviços
                      </button>
                    </div>
                  </div>
                  <form onSubmit={handleSubmit} className="flex space-x-2">
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder={`Pergunte algo sobre ${agentType === 'GERAL' ? 'Recife' :
                          agentType === 'CULTURA' ? 'eventos culturais' :
                            agentType === 'SAUDE' ? 'saúde pública' :
                              agentType === 'MOBILIDADE' ? 'mobilidade urbana' : 'serviços municipais'
                        }...`}
                      className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      type="submit"
                      disabled={loading}
                      className={`px-4 py-2 rounded-lg flex items-center justify-center ${loading
                          ? 'bg-gray-300 text-gray-500'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                        }`}
                    >
                      <MessageSquare size={18} className="mr-2" />
                      Enviar
                    </button>
                  </form>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <button
                      onClick={() => {
                        setQuery("Quais áreas têm mais eventos culturais?");
                      }}
                      className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-lg border border-blue-100 hover:bg-blue-100"
                    >
                      Quais áreas têm mais eventos culturais?
                    </button>
                    <button
                      onClick={() => {
                        setQuery("Onde encontro academias públicas perto de mim?");
                      }}
                      className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-lg border border-blue-100 hover:bg-blue-100"
                    >
                      Onde encontro academias públicas perto de mim?
                    </button>
                    <button
                      onClick={() => {
                        setQuery("Como está a mobilidade urbana no Recife?");
                      }}
                      className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-lg border border-blue-100 hover:bg-blue-100"
                    >
                      Como está a mobilidade urbana no Recife?
                    </button>
                    <button
                      onClick={() => {
                        setQuery("Onde posso resolver problemas com IPTU?");
                      }}
                      className="text-xs bg-blue-50 text-blue-600 px-2 py-1 rounded-lg border border-blue-100 hover:bg-blue-100"
                    >
                      Onde posso resolver problemas com IPTU?
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Quick access grid - Now below the chat section */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">Explorar Dados por Categoria</h2>
                <a href="#" className="text-blue-600 hover:underline text-sm flex items-center">
                  Ver todos <ArrowRight size={16} className="ml-1" />
                </a>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-green-50 rounded-lg p-4 border border-green-100 hover:shadow-md transition-shadow">
                  <div className="h-10 w-10 bg-green-100 rounded-full flex items-center justify-center mb-3">
                    <Activity size={20} className="text-green-600" />
                  </div>
                  <h3 className="font-medium text-green-800 mb-1">Saúde</h3>
                  <p className="text-sm text-gray-600 mb-3">Dados sobre saúde pública, unidades de atendimento e campanhas.</p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">23 datasets</span>
                    <button className="text-green-600 hover:bg-green-100 p-1 rounded">
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </div>

                <div className="bg-blue-50 rounded-lg p-4 border border-blue-100 hover:shadow-md transition-shadow">
                  <div className="h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                    <Map size={20} className="text-blue-600" />
                  </div>
                  <h3 className="font-medium text-blue-800 mb-1">Mobilidade</h3>
                  <p className="text-sm text-gray-600 mb-3">Informações sobre transporte público, ciclovias e trânsito.</p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">45 datasets</span>
                    <button className="text-blue-600 hover:bg-blue-100 p-1 rounded">
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </div>

                <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-100 hover:shadow-md transition-shadow">
                  <div className="h-10 w-10 bg-yellow-100 rounded-full flex items-center justify-center mb-3">
                    <BookOpen size={20} className="text-yellow-600" />
                  </div>
                  <h3 className="font-medium text-yellow-800 mb-1">Educação</h3>
                  <p className="text-sm text-gray-600 mb-3">Dados sobre escolas, programas educacionais e bibliotecas.</p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">31 datasets</span>
                    <button className="text-yellow-600 hover:bg-yellow-100 p-1 rounded">
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </div>

                <div className="bg-purple-50 rounded-lg p-4 border border-purple-100 hover:shadow-md transition-shadow">
                  <div className="h-10 w-10 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                    <Calendar size={20} className="text-purple-600" />
                  </div>
                  <h3 className="font-medium text-purple-800 mb-1">Cultura</h3>
                  <p className="text-sm text-gray-600 mb-3">Eventos culturais, equipamentos culturais e patrimônio histórico.</p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-500">27 datasets</span>
                    <button className="text-purple-600 hover:bg-purple-100 p-1 rounded">
                      <ArrowRight size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Recently Updated Data */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold text-gray-800">Dados Recentemente Atualizados</h2>
                <a href="#" className="text-blue-600 hover:underline text-sm flex items-center">
                  Ver todos <ArrowRight size={16} className="ml-1" />
                </a>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-center mb-3">
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Mobilidade</span>
                    <span className="text-xs text-gray-500">Atualizado há 2 dias</span>
                  </div>
                  <h3 className="font-medium text-gray-800 mb-2">Ciclovias do Recife</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Mapeamento completo da malha cicloviária da cidade, incluindo extensão, condições e conectividade.
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center text-xs text-gray-500">
                      <Download size={14} className="mr-1" />
                      523 downloads
                    </span>
                    <button className="text-blue-600 hover:bg-blue-50 p-1 rounded">
                      Visualizar
                    </button>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-center mb-3">
                    <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Saúde</span>
                    <span className="text-xs text-gray-500">Atualizado há 3 dias</span>
                  </div>
                  <h3 className="font-medium text-gray-800 mb-2">Unidades de Saúde</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Informações sobre postos de saúde, hospitais e clínicas públicas, incluindo serviços e horários.
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center text-xs text-gray-500">
                      <Download size={14} className="mr-1" />
                      782 downloads
                    </span>
                    <button className="text-blue-600 hover:bg-blue-50 p-1 rounded">
                      Visualizar
                    </button>
                  </div>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-center mb-3">
                    <span className="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">Cultura</span>
                    <span className="text-xs text-gray-500">Atualizado há 5 dias</span>
                  </div>
                  <h3 className="font-medium text-gray-800 mb-2">Agenda Cultural</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Programação de eventos culturais, shows, exposições e atividades gratuitas na cidade.
                  </p>
                  <div className="flex justify-between items-center">
                    <span className="flex items-center text-xs text-gray-500">
                      <Download size={14} className="mr-1" />
                      1,203 downloads
                    </span>
                    <button className="text-blue-600 hover:bg-blue-50 p-1 rounded">
                      Visualizar
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* How It Works Modal */}
      {showHowItWorks && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold text-blue-800">Como Funciona a IA de Dados do Recife</h2>
                <button 
                  onClick={() => setShowHowItWorks(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <span className="text-2xl">&times;</span>
                </button>
              </div>
            </div>

            <div className="p-6">
              <div className="flex flex-col items-center mb-6">
                <div className="w-full max-w-3xl bg-blue-50 rounded-xl p-4 text-center mb-6">
                  <p className="text-blue-800 text-lg font-medium">Transformando suas perguntas em dados úteis e relevantes</p>
                  <p className="text-blue-600">Tecnologia avançada para democratizar o acesso a informações sobre o Recife</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
                {/* Step 1 */}
                <div className="bg-gray-50 rounded-lg p-4 text-center flex flex-col items-center">
                  <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                    <MessageSquare size={20} className="text-blue-600" />
                  </div>
                  <h3 className="font-medium text-gray-800 mb-1">Sua Pergunta</h3>
                  <p className="text-xs text-gray-600">Pergunte em linguagem natural</p>
                </div>

                {/* Arrow */}
                <div className="hidden md:flex items-center justify-center">
                  <ArrowRight size={24} className="text-gray-400" />
                </div>

                {/* Step 2 */}
                <div className="bg-gray-50 rounded-lg p-4 text-center flex flex-col items-center">
                  <div className="h-12 w-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                    <Layers size={20} className="text-purple-600" />
                  </div>
                  <h3 className="font-medium text-gray-800 mb-1">Seleção do Agente</h3>
                  <p className="text-xs text-gray-600">O sistema identifica o especialista</p>
                </div>

                {/* Arrow */}
                <div className="hidden md:flex items-center justify-center">
                  <ArrowRight size={24} className="text-gray-400" />
                </div>

                {/* Step 3 */}
                <div className="bg-gray-50 rounded-lg p-4 text-center flex flex-col items-center">
                  <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center mb-3">
                    <Search size={20} className="text-green-600" />
                  </div>
                  <h3 className="font-medium text-gray-800 mb-1">Busca nos Dados</h3>
                  <p className="text-xs text-gray-600">Consulta em +200 bases de dados</p>
                </div>
              </div>

              <div className="bg-gray-50 rounded-xl p-6 mb-6">
                <h3 className="font-bold text-lg text-gray-800 mb-4">Fluxo de Processamento</h3>
                <div className="flex flex-col space-y-4">
                  <div className="flex items-start space-x-4">
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="font-bold text-blue-600">1</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Identificação do Agente</h4>
                      <p className="text-sm text-gray-600">Seu input é analisado para determinar se é uma questão de CULTURA, SAÚDE, MOBILIDADE ou SERVIÇOS, direcionando ao agente especializado.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="font-bold text-blue-600">2</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Conexão com APIs</h4>
                      <p className="text-sm text-gray-600">O sistema se integra diretamente com a API do dados.recife, acessando mais de 200 bases de dados da cidade.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="font-bold text-blue-600">3</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Transformação em SQL</h4>
                      <p className="text-sm text-gray-600">Sua pergunta em linguagem natural é convertida em uma consulta SQL estruturada que pode ser executada nas bases de dados.</p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-4">
                    <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                      <span className="font-bold text-blue-600">4</span>
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-800">Filtragem Inteligente</h4>
                      <p className="text-sm text-gray-600">O sistema filtra os campos relevantes no dataset com base no contexto da sua pergunta para fornecer a informação mais precisa.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-purple-50 rounded-lg p-4 border border-purple-100">
                  <div className="flex items-center mb-3">
                    <Calendar size={18} className="text-purple-600 mr-2" />
                    <h4 className="font-medium text-purple-800">Agente Cultural</h4>
                  </div>
                  <p className="text-sm text-gray-600">Especializado em eventos, patrimônio histórico e manifestações culturais do Recife.</p>
                </div>

                <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                  <div className="flex items-center mb-3">
                    <Heart size={18} className="text-green-600 mr-2" />
                    <h4 className="font-medium text-green-800">Agente de Saúde</h4>
                  </div>
                  <p className="text-sm text-gray-600">Informações sobre unidades de saúde, campanhas e serviços médicos disponíveis.</p>
                </div>

                <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                  <div className="flex items-center mb-3">
                    <Bus size={18} className="text-blue-600 mr-2" />
                    <h4 className="font-medium text-blue-800">Agente de Mobilidade</h4>
                  </div>
                  <p className="text-sm text-gray-600">Dados sobre transporte público, trânsito, ciclovias e infraestrutura urbana.</p>
                </div>

                <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-100">
                  <div className="flex items-center mb-3">
                    <Briefcase size={18} className="text-yellow-600 mr-2" />
                    <h4 className="font-medium text-yellow-800">Agente de Serviços</h4>
                  </div>
                  <p className="text-sm text-gray-600">Informações sobre serviços municipais, documentos, tributos e atendimento ao cidadão.</p>
                </div>
              </div>

              <div className="flex justify-center">
                <button 
                  onClick={() => setShowHowItWorks(false)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                >
                  Entendi
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      
    </div>
  );
};

export default App;