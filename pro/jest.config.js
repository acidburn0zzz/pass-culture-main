module.exports = {
  moduleNameMapper: {
    '\\.(png|svg)': '<rootDir>/src/utils/svgrMock.js',
    '\\.module\\.scss$': 'identity-obj-proxy',
    '\\.(css|less|scss|sass)$': '<rootDir>/src/utils/styleMock.js',
    '@fontsource/barlow': '<rootDir>/src/utils/styleMock.js',
  },
  modulePaths: ['node_modules', 'src'],
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts', 'jest-canvas-mock'],
  testEnvironment: 'jsdom',
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
    // '<rootDir>/eslint-plugin-pass-culture/**/*.{spec,test}.{js,jsx,ts,tsx}',
    '<rootDir>/stylelint-pass-culture/**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  verbose: false,
  clearMocks: true,
  restoreMocks: true,
  testTimeout: 30000,
  cacheDirectory: '.jest_cache',
}
