import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { User, Mail, Building, Calendar, Edit2, Save, X } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Profile() {
  const { user, updateProfile } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    organization: user?.organization || ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    updateProfile(formData);
    setIsEditing(false);
    toast.success('Profile updated successfully!');
  };

  const handleCancel = () => {
    setFormData({
      name: user?.name || '',
      organization: user?.organization || ''
    });
    setIsEditing(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
        <p className="text-gray-600 mt-2">Manage your account information</p>
      </div>

      {/* Profile Card */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        {/* Header Section */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-20 h-20 bg-[#2D6A4F] rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-white">
                  {user?.name?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{user?.name}</h2>
                <p className="text-gray-600">{user?.email}</p>
              </div>
            </div>
            {!isEditing && (
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center px-4 py-2 text-[#2D6A4F] hover:bg-gray-50 rounded-lg transition-colors"
              >
                <Edit2 size={18} className="mr-2" />
                Edit Profile
              </button>
            )}
          </div>
        </div>

        {/* Profile Information */}
        <div className="p-6">
          {isEditing ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#40916C] focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Organization
                </label>
                <input
                  type="text"
                  value={formData.organization}
                  onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#40916C] focus:border-transparent"
                  placeholder="Company or organization name"
                />
              </div>

              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex items-center px-4 py-2 bg-[#2D6A4F] text-white rounded-lg hover:bg-[#1B4332] transition-colors"
                >
                  <Save size={18} className="mr-2" />
                  Save Changes
                </button>
                <button
                  type="button"
                  onClick={handleCancel}
                  className="flex items-center px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <X size={18} className="mr-2" />
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <User className="text-gray-400 mt-1" size={20} />
                <div>
                  <p className="text-sm text-gray-600">Full Name</p>
                  <p className="text-gray-900 font-medium">{user?.name}</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Mail className="text-gray-400 mt-1" size={20} />
                <div>
                  <p className="text-sm text-gray-600">Email Address</p>
                  <p className="text-gray-900 font-medium">{user?.email}</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Building className="text-gray-400 mt-1" size={20} />
                <div>
                  <p className="text-sm text-gray-600">Organization</p>
                  <p className="text-gray-900 font-medium">{user?.organization || 'Not specified'}</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <Calendar className="text-gray-400 mt-1" size={20} />
                <div>
                  <p className="text-sm text-gray-600">Member Since</p>
                  <p className="text-gray-900 font-medium">
                    {new Date(user?.createdAt).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Account Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Actions</h3>
        <div className="space-y-3">
          <button className="w-full px-4 py-3 text-left text-gray-700 hover:bg-gray-50 rounded-lg transition-colors border border-gray-200">
            Change Password
          </button>
          <button className="w-full px-4 py-3 text-left text-red-600 hover:bg-red-50 rounded-lg transition-colors border border-red-200">
            Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}
