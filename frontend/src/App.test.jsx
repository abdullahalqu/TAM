import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import App from './App'

describe('App Component', () => {
  it('renders without crashing', () => {
    const { container } = render(<App />)
    expect(container).toBeTruthy()
  })

  it('renders the application', () => {
    const { container } = render(<App />)
    // App should render something
    expect(container.firstChild).toBeTruthy()
  })
})
