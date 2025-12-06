'use client';

import { FormEvent, useEffect, useState } from 'react';

type Employee = {
  id: number;
  name: string;
  lastname: string;
  salary: number;
  address: string;
  in_vacation: boolean;
};

type EmployeePayload = Omit<Employee, 'id'>;

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const initialForm: EmployeePayload = {
  name: '',
  lastname: '',
  salary: 0,
  address: '',
  in_vacation: false,
};

export default function Home() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [form, setForm] = useState<EmployeePayload>(initialForm);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/employees`);
      if (!res.ok) {
        throw new Error('No se pudieron cargar los empleados');
      }
      const data = await res.json();
      setEmployees(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const url = editingId ? `${API_URL}/employees/${editingId}` : `${API_URL}/employees`;
    const method = editingId ? 'PUT' : 'POST';

    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      if (!res.ok) {
        throw new Error('No se pudo guardar el empleado');
      }

      await fetchEmployees();
      setForm(initialForm);
      setEditingId(null);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (employee: Employee) => {
    setForm({
      name: employee.name,
      lastname: employee.lastname,
      salary: employee.salary,
      address: employee.address,
      in_vacation: employee.in_vacation,
    });
    setEditingId(employee.id);
  };

  const handleDelete = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/employees/${id}`, { method: 'DELETE' });
      if (!res.ok) {
        throw new Error('No se pudo eliminar el empleado');
      }
      await fetchEmployees();
      if (editingId === id) {
        setForm(initialForm);
        setEditingId(null);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleInput = (
    field: keyof EmployeePayload,
    value: string | boolean,
  ) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <main style={{ padding: '2rem', maxWidth: 900, margin: '0 auto' }}>
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ margin: 0 }}>Gestor de Empleados</h1>
        <p style={{ marginTop: '0.25rem', color: '#475569' }}>
          CRUD básico usando FastAPI y SQLite en el backend.
        </p>
      </header>

      <section
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1.2fr',
          gap: '1.5rem',
          alignItems: 'start',
        }}
      >
        <form
          onSubmit={handleSubmit}
          style={{
            padding: '1.5rem',
            background: '#fff',
            borderRadius: '12px',
            boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)',
          }}
        >
          <h2 style={{ marginTop: 0 }}>{editingId ? 'Editar' : 'Crear'} empleado</h2>
          <div style={{ display: 'grid', gap: '0.75rem' }}>
            <label style={{ display: 'grid', gap: '0.35rem' }}>
              <span>Nombre</span>
              <input
                required
                type="text"
                value={form.name}
                onChange={(e) => handleInput('name', e.target.value)}
              />
            </label>
            <label style={{ display: 'grid', gap: '0.35rem' }}>
              <span>Apellido</span>
              <input
                required
                type="text"
                value={form.lastname}
                onChange={(e) => handleInput('lastname', e.target.value)}
              />
            </label>
            <label style={{ display: 'grid', gap: '0.35rem' }}>
              <span>Salario</span>
              <input
                required
                type="number"
                min="0"
                value={form.salary}
                onChange={(e) => handleInput('salary', Number(e.target.value))}
              />
            </label>
            <label style={{ display: 'grid', gap: '0.35rem' }}>
              <span>Dirección</span>
              <input
                required
                type="text"
                value={form.address}
                onChange={(e) => handleInput('address', e.target.value)}
              />
            </label>
            <label style={{ display: 'inline-flex', gap: '0.5rem', alignItems: 'center' }}>
              <input
                type="checkbox"
                checked={form.in_vacation}
                onChange={(e) => handleInput('in_vacation', e.target.checked)}
              />
              <span>En vacaciones</span>
            </label>
            <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: '0.75rem 1.25rem',
                  background: '#2563eb',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                }}
              >
                {editingId ? 'Actualizar' : 'Crear'}
              </button>
              {editingId && (
                <button
                  type="button"
                  onClick={() => {
                    setEditingId(null);
                    setForm(initialForm);
                  }}
                  style={{
                    padding: '0.75rem 1rem',
                    background: '#e2e8f0',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                  }}
                >
                  Cancelar
                </button>
              )}
            </div>
            {error && <p style={{ color: '#b91c1c' }}>{error}</p>}
          </div>
        </form>

        <div
          style={{
            background: '#fff',
            padding: '1.5rem',
            borderRadius: '12px',
            boxShadow: '0 10px 30px rgba(15, 23, 42, 0.08)',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0 }}>Empleados</h2>
            <button
              type="button"
              onClick={fetchEmployees}
              disabled={loading}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                border: '1px solid #cbd5e1',
                background: '#f8fafc',
                cursor: 'pointer',
              }}
            >
              Recargar
            </button>
          </div>
          {loading && <p>Cargando...</p>}
          {!loading && employees.length === 0 && <p>No hay empleados registrados.</p>}
          {!loading && employees.length > 0 && (
            <table style={{ width: '100%', marginTop: '1rem', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ textAlign: 'left', borderBottom: '1px solid #e2e8f0' }}>
                  <th style={{ padding: '0.5rem' }}>ID</th>
                  <th style={{ padding: '0.5rem' }}>Nombre</th>
                  <th style={{ padding: '0.5rem' }}>Apellido</th>
                  <th style={{ padding: '0.5rem' }}>Salario</th>
                  <th style={{ padding: '0.5rem' }}>Dirección</th>
                  <th style={{ padding: '0.5rem' }}>Vacaciones</th>
                  <th style={{ padding: '0.5rem' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((employee) => (
                  <tr key={employee.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '0.5rem' }}>{employee.id}</td>
                    <td style={{ padding: '0.5rem' }}>{employee.name}</td>
                    <td style={{ padding: '0.5rem' }}>{employee.lastname}</td>
                    <td style={{ padding: '0.5rem' }}>${employee.salary.toFixed(2)}</td>
                    <td style={{ padding: '0.5rem' }}>{employee.address}</td>
                    <td style={{ padding: '0.5rem' }}>
                      {employee.in_vacation ? 'Sí' : 'No'}
                    </td>
                    <td style={{ padding: '0.5rem', display: 'flex', gap: '0.5rem' }}>
                      <button
                        type="button"
                        onClick={() => handleEdit(employee)}
                        style={{
                          padding: '0.35rem 0.75rem',
                          background: '#10b981',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                        }}
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(employee.id)}
                        style={{
                          padding: '0.35rem 0.75rem',
                          background: '#ef4444',
                          color: '#fff',
                          border: 'none',
                          borderRadius: '6px',
                          cursor: 'pointer',
                        }}
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </section>
    </main>
  );
}
