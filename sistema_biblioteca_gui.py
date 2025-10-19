#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import json
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import darkdetect

class BibliotecaApp:
    def __init__(self):
        self.tema = "darkly" if darkdetect.isDark() else "flatly"
        self.app = tb.Window(themename=self.tema)
        self.app.title("Sistema de Biblioteca")
        self.app.geometry("800x600")
        self.app.resizable(True, True)
        
        self.biblioteca = self.carregar_biblioteca()
        self.criar_interface()
        self.atualizar_tabela()
        
    def criar_interface(self):
        self.frame_principal = ttk.Frame(self.app, padding=20)
        self.frame_principal.pack(fill="both", expand=True)
        
        titulo_label = tb.Label(
            self.frame_principal, 
            text="Minha Biblioteca", 
            font=("Helvetica", 16, "bold"),
            bootstyle="primary"
        )
        titulo_label.pack(pady=(0, 20))
        
        self.criar_secao_entrada()
        self.criar_secao_botoes()
        self.criar_tabela()
        self.criar_status_bar()
    
    def criar_secao_entrada(self):
        frame_entrada = tb.LabelFrame(
            self.frame_principal, 
            text="Cadastrar Novo Livro",
            bootstyle="primary",
            padding=15
        )
        frame_entrada.pack(fill="x", pady=(0, 15))
        
        campos = [
            ("Titulo:", "entry_titulo", 40),
            ("Autor:", "entry_autor", 40),
            ("Ano:", "entry_ano", 15),
            ("Paginas:", "entry_paginas", 15)
        ]
        
        for i, (label_text, attr_name, width) in enumerate(campos):
            label = tb.Label(frame_entrada, text=label_text, bootstyle="primary")
            label.grid(row=i, column=0, sticky="w", padx=(0, 10), pady=5)
            
            entry = tb.Entry(frame_entrada, width=width, font=("Segoe UI", 10))
            entry.grid(row=i, column=1, sticky="w", pady=5)
            
            setattr(self, attr_name, entry)
    
    def criar_secao_botoes(self):
        frame_botoes = ttk.Frame(self.frame_principal)
        frame_botoes.pack(pady=10)
        
        botoes = [
            ("Cadastrar Livro", self.adicionar_livro, "success"),
            ("Atualizar Livro", self.atualizar_livro, "info"),
            ("Remover Livro", self.remover_livro, "danger"),
            ("Ver Estatisticas", self.mostrar_estatisticas, "warning"),
            ("Salvar Dados", self.salvar_biblioteca, "secondary")
        ]
        
        for texto, comando, estilo in botoes:
            btn = tb.Button(
                frame_botoes, 
                text=texto, 
                command=comando, 
                bootstyle=estilo,
                width=15
            )
            btn.pack(side="left", padx=5)
    
    def criar_tabela(self):
        frame_tabela = tb.LabelFrame(
            self.frame_principal, 
            text="Livros Cadastrados",
            bootstyle="primary",
            padding=10
        )
        frame_tabela.pack(fill="both", expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(frame_tabela)
        scrollbar.pack(side="right", fill="y")
        
        colunas = ("Titulo", "Autor", "Ano", "Paginas")
        self.tabela = ttk.Treeview(
            frame_tabela, 
            columns=colunas, 
            show="headings", 
            height=12,
            yscrollcommand=scrollbar.set,
            bootstyle="primary"
        )
        
        larguras = [300, 200, 100, 100]
        for col, largura in zip(colunas, larguras):
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=largura, minwidth=80)
        
        self.tabela.pack(fill="both", expand=True)
        scrollbar.config(command=self.tabela.yview)
        
        self.tabela.bind("<Double-1>", self.preencher_campos_ao_clicar)
    
    def criar_status_bar(self):
        self.status_bar = tb.Label(
            self.frame_principal,
            text=f"Total de livros: {len(self.biblioteca)}",
            bootstyle="secondary",
            relief="sunken",
            anchor="center"
        )
        self.status_bar.pack(fill="x", side="bottom")
    
    def carregar_biblioteca(self):
        try:
            with open("biblioteca.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Arquivo de biblioteca corrompido!")
            return []
    
    def salvar_biblioteca(self):
        try:
            with open("biblioteca.json", "w", encoding="utf-8") as f:
                json.dump(self.biblioteca, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Sucesso", "Biblioteca salva com sucesso!")
            self.atualizar_status_bar()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
    
    def atualizar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        for livro in self.biblioteca:
            self.tabela.insert("", "end", values=(
                livro["titulo"], 
                livro["autor"], 
                livro["ano"], 
                livro["paginas"]
            ))
        
        self.atualizar_status_bar()
    
    def atualizar_status_bar(self):
        self.status_bar.config(text=f"Total de livros: {len(self.biblioteca)}")
    
    def adicionar_livro(self):
        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()
        ano = self.entry_ano.get().strip()
        paginas = self.entry_paginas.get().strip()

        if not all([titulo, autor, ano, paginas]):
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return
        
        if not ano.isdigit():
            messagebox.showwarning("Aviso", "Ano deve ser um numero!")
            return
        
        if not paginas.isdigit():
            messagebox.showwarning("Aviso", "Paginas deve ser um numero!")
            return

        if any(livro["titulo"].lower() == titulo.lower() for livro in self.biblioteca):
            messagebox.showwarning("Aviso", "Este livro ja esta cadastrado!")
            return

        self.biblioteca.append({
            "titulo": titulo, 
            "autor": autor, 
            "ano": ano, 
            "paginas": paginas
        })
        
        self.salvar_biblioteca()
        self.atualizar_tabela()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", "Livro adicionado com sucesso!")

    def remover_livro(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showinfo("Info", "Selecione um livro para remover.")
            return
        
        item = self.tabela.item(selecionado[0])
        titulo = item["values"][0]
        
        resposta = messagebox.askyesno(
            "Confirmar", 
            f"Tem certeza que deseja remover o livro:\n\"{titulo}\"?"
        )
        
        if resposta:
            self.biblioteca = [livro for livro in self.biblioteca if livro["titulo"] != titulo]
            self.salvar_biblioteca()
            self.atualizar_tabela()
            messagebox.showinfo("Sucesso", "Livro removido com sucesso!")

    def atualizar_livro(self):
        selecionado = self.tabela.selection()
        if not selecionado:
            messagebox.showinfo("Info", "Selecione um livro para atualizar.")
            return

        item = self.tabela.item(selecionado[0])
        titulo_original = item["values"][0]

        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()
        ano = self.entry_ano.get().strip()
        paginas = self.entry_paginas.get().strip()

        if not all([titulo, autor, ano, paginas]):
            messagebox.showwarning("Aviso", "Preencha todos os campos!")
            return

        if (titulo.lower() != titulo_original.lower() and 
            any(livro["titulo"].lower() == titulo.lower() for livro in self.biblioteca)):
            messagebox.showwarning("Aviso", "Ja existe um livro com este titulo!")
            return

        for livro in self.biblioteca:
            if livro["titulo"] == titulo_original:
                livro.update({
                    "titulo": titulo,
                    "autor": autor,
                    "ano": ano,
                    "paginas": paginas
                })
                break

        self.salvar_biblioteca()
        self.atualizar_tabela()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", "Livro atualizado com sucesso!")

    def limpar_campos(self):
        self.entry_titulo.delete(0, tk.END)
        self.entry_autor.delete(0, tk.END)
        self.entry_ano.delete(0, tk.END)
        self.entry_paginas.delete(0, tk.END)

    def mostrar_estatisticas(self):
        total = len(self.biblioteca)
        if total == 0:
            messagebox.showinfo("Estatisticas", "Nenhum livro cadastrado.")
            return
        
        paginas_validas = [int(l["paginas"]) for l in self.biblioteca if l["paginas"].isdigit()]
        media_paginas = sum(paginas_validas) / len(paginas_validas) if paginas_validas else 0
        
        anos_validos = [int(l["ano"]) for l in self.biblioteca if l["ano"].isdigit() and 1000 <= int(l["ano"]) <= 2100]
        ano_mais_antigo = min(anos_validos) if anos_validos else "N/A"
        ano_mais_novo = max(anos_validos) if anos_validos else "N/A"
        
        autores_unicos = len(set(livro["autor"].lower() for livro in self.biblioteca))
        
        estatisticas = f"""Estatisticas da Biblioteca:

Total de livros: {total}
Autores diferentes: {autores_unicos}
Media de paginas: {media_paginas:.1f}
Livro mais antigo: {ano_mais_antigo}
Livro mais recente: {ano_mais_novo}"""
        
        messagebox.showinfo("Estatisticas", estatisticas)

    def preencher_campos_ao_clicar(self, event):
        selecionado = self.tabela.selection()
        if selecionado:
            item = self.tabela.item(selecionado[0])
            valores = item["values"]
            
            self.limpar_campos()
            self.entry_titulo.insert(0, valores[0])
            self.entry_autor.insert(0, valores[1])
            self.entry_ano.insert(0, valores[2])
            self.entry_paginas.insert(0, valores[3])

    def executar(self):
        self.app.mainloop()

if __name__ == "__main__":
    app = BibliotecaApp()
    app.executar()