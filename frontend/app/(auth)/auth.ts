import { compare } from 'bcrypt-ts'; // Import bcrypt-ts to compare hashed passwords.
import NextAuth, { type User, type Session } from 'next-auth'; // Import NextAuth for authentication setup and types for User and Session.
import Credentials from 'next-auth/providers/credentials'; // Import the credentials provider for custom authentication logic.

import { getUser } from '@/lib/db/queries'; // Import a custom query function to fetch user data from your database.

import { authConfig } from './auth.config'; // Import additional authentication configuration.

interface ExtendedSession extends Session {
  user: User; // Extend the session object to include full user information.
}

// Export authentication handlers (GET, POST) and utilities (auth, signIn, signOut).
export const {
  handlers: { GET, POST }, // Handlers for authentication-related HTTP requests (GET for session, POST for sign-in).
  auth, // The main authentication function.
  signIn, // Utility to programmatically sign in users.
  signOut, // Utility to programmatically sign out users.
} = NextAuth({
  ...authConfig, // Spread the additional authentication configurations.
  trustHost: true, //This is not safe TODO: Fix this for production
  providers: [
    // Define authentication providers. In this case, using custom credentials.
    Credentials({
      credentials: {}, // No predefined credentials; fields will be dynamically provided.
      async authorize({ email, password }: any) {
        // Custom function to authenticate users.
        const users = await getUser(email); // Fetch user data by email from the database.
        if (users.length === 0) return null; // If no user is found, return null (authentication fails).

        // Compare the provided password with the stored hashed password.
        // biome-ignore lint: Forbidden non-null assertion.
        const passwordsMatch = await compare(password, users[0].password!);
        if (!passwordsMatch) return null; // If passwords do not match, return null.

        // If authentication succeeds, return the user object.
        return users[0] as any;
      },
    }),
  ],
  callbacks: {
    // Callbacks are used to extend or modify the behavior of NextAuth.
    async jwt({ token, user }) {
      // JWT callback runs when a token is created or updated.
      if (user) {
        token.id = user.id; // Add the user ID to the token if available.
      }

      return token; // Return the updated token.
    },
    async session({
      session, // The current session object.
      token, // The token containing additional user information.
    }: {
      session: ExtendedSession; // Extended session type that includes the user.
      token: any; // The token object (customizable based on your application needs).
    }) {
      if (session.user) {
        session.user.id = token.id as string; // Attach the user ID from the token to the session object.
      }

      return session; // Return the updated session.
    },
  },
});
