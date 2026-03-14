"use client";

import { useState, useRef, useEffect } from "react";
import { FolderOpen, Plus, ChevronDown, Trash2, Pencil, X, Check } from "lucide-react";

import type { ProjectSummary } from "@/domain/entities/ProjectSummary";

interface ProjectSelectorProps {
  projects: ProjectSummary[];
  activeProjectId: string | null;
  isLoading: boolean;
  onSelectProject: (id: string | null) => void;
  onCreateProject: (name: string) => void;
  onDeleteProject: (id: string) => void;
  onRenameProject: (id: string, name: string) => void;
}

export default function ProjectSelector({
  projects,
  activeProjectId,
  isLoading,
  onSelectProject,
  onCreateProject,
  onDeleteProject,
  onRenameProject,
}: ProjectSelectorProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);
  const createInputRef = useRef<HTMLInputElement>(null);
  const editInputRef = useRef<HTMLInputElement>(null);

  const activeProject = projects.find((p) => p.id === activeProjectId);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
        setIsCreating(false);
        setEditingId(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Focus inputs when shown
  useEffect(() => {
    if (isCreating) createInputRef.current?.focus();
  }, [isCreating]);

  useEffect(() => {
    if (editingId) editInputRef.current?.focus();
  }, [editingId]);

  const handleCreate = () => {
    const trimmed = newProjectName.trim();
    if (!trimmed) return;
    onCreateProject(trimmed);
    setNewProjectName("");
    setIsCreating(false);
  };

  const handleRename = (id: string) => {
    const trimmed = editingName.trim();
    if (!trimmed) return;
    onRenameProject(id, trimmed);
    setEditingId(null);
  };

  return (
    <div className="relative px-3 py-2 border-b" style={{ borderColor: "var(--border)" }} ref={dropdownRef}>
      {/* Trigger button */}
      <button
        onClick={() => setIsDropdownOpen((prev) => !prev)}
        className="flex items-center justify-between w-full px-2.5 py-2 rounded-lg text-sm transition-colors cursor-pointer"
        style={{
          background: "var(--bg-tertiary)",
          color: "var(--text-primary)",
        }}
      >
        <span className="flex items-center gap-2 truncate">
          <FolderOpen size={14} style={{ color: "var(--text-secondary)" }} />
          <span className="truncate">
            {activeProject ? activeProject.name : "All Conversations"}
          </span>
        </span>
        <ChevronDown
          size={14}
          style={{
            color: "var(--text-secondary)",
            transform: isDropdownOpen ? "rotate(180deg)" : "none",
            transition: "transform 150ms",
          }}
        />
      </button>

      {/* Dropdown */}
      {isDropdownOpen && (
        <div
          className="absolute left-3 right-3 mt-1 rounded-lg shadow-lg z-50 overflow-hidden"
          style={{
            background: "var(--bg-primary)",
            border: "1px solid var(--border)",
          }}
        >
          {/* "All Conversations" option */}
          <button
            onClick={() => {
              onSelectProject(null);
              setIsDropdownOpen(false);
            }}
            className="flex items-center gap-2 w-full px-3 py-2 text-sm text-left transition-colors cursor-pointer"
            style={{
              background: activeProjectId === null ? "var(--bg-tertiary)" : "transparent",
              color: "var(--text-primary)",
            }}
          >
            All Conversations
          </button>

          {/* Divider */}
          <div className="h-px mx-2" style={{ background: "var(--border)" }} />

          {/* Project list */}
          {isLoading ? (
            <div className="px-3 py-2">
              <div className="h-6 rounded animate-pulse" style={{ background: "var(--bg-tertiary)" }} />
            </div>
          ) : (
            projects.map((project) => (
              <div
                key={project.id}
                className="flex items-center group"
                style={{
                  background: project.id === activeProjectId ? "var(--bg-tertiary)" : "transparent",
                }}
              >
                {editingId === project.id ? (
                  <div className="flex items-center gap-1 flex-1 px-2 py-1.5">
                    <input
                      ref={editInputRef}
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleRename(project.id);
                        if (e.key === "Escape") setEditingId(null);
                      }}
                      className="flex-1 text-sm px-2 py-0.5 rounded outline-none"
                      style={{
                        background: "var(--bg-secondary)",
                        color: "var(--text-primary)",
                        border: "1px solid var(--border)",
                      }}
                    />
                    <button
                      onClick={() => handleRename(project.id)}
                      className="p-1 rounded cursor-pointer"
                      style={{ color: "var(--accent)" }}
                    >
                      <Check size={13} />
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="p-1 rounded cursor-pointer"
                      style={{ color: "var(--text-secondary)" }}
                    >
                      <X size={13} />
                    </button>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => {
                        onSelectProject(project.id);
                        setIsDropdownOpen(false);
                      }}
                      className="flex-1 text-left px-3 py-2 text-sm truncate transition-colors cursor-pointer"
                      style={{ color: "var(--text-primary)" }}
                    >
                      {project.name}
                    </button>
                    <div className="hidden group-hover:flex items-center gap-0.5 pr-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingId(project.id);
                          setEditingName(project.name);
                        }}
                        className="p-1 rounded transition-colors cursor-pointer"
                        style={{ color: "var(--text-secondary)" }}
                        title="Rename project"
                      >
                        <Pencil size={12} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteProject(project.id);
                        }}
                        className="p-1 rounded transition-colors cursor-pointer"
                        style={{ color: "var(--error)" }}
                        title="Delete project"
                      >
                        <Trash2 size={12} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          )}

          {/* Divider */}
          <div className="h-px mx-2" style={{ background: "var(--border)" }} />

          {/* Create new project */}
          {isCreating ? (
            <div className="flex items-center gap-1 px-2 py-2">
              <input
                ref={createInputRef}
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleCreate();
                  if (e.key === "Escape") {
                    setIsCreating(false);
                    setNewProjectName("");
                  }
                }}
                placeholder="Project name..."
                className="flex-1 text-sm px-2 py-1 rounded outline-none"
                style={{
                  background: "var(--bg-secondary)",
                  color: "var(--text-primary)",
                  border: "1px solid var(--border)",
                }}
              />
              <button
                onClick={handleCreate}
                className="p-1 rounded cursor-pointer"
                style={{ color: "var(--accent)" }}
              >
                <Check size={14} />
              </button>
              <button
                onClick={() => {
                  setIsCreating(false);
                  setNewProjectName("");
                }}
                className="p-1 rounded cursor-pointer"
                style={{ color: "var(--text-secondary)" }}
              >
                <X size={14} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsCreating(true)}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm transition-colors cursor-pointer"
              style={{ color: "var(--accent)" }}
            >
              <Plus size={14} />
              New Project
            </button>
          )}
        </div>
      )}
    </div>
  );
}
